import httpx

from ion_client.logger import logger
from ion_client.sso import SSOClient


class Client:
    DEFAULT_API_VERSION = 14
    DEFAULT_BASE_URL = "https://nb.portal.arubainstanton.com/api"

    def __init__(
        self,
        username: str,
        password: str,
        otp: str | None = None,
        api_version: int = DEFAULT_API_VERSION,
        base_url: str = DEFAULT_BASE_URL,
        sso: SSOClient | None = None,
    ):
        self.username = username
        self.password = password
        self.otp = otp
        if not sso:
            sso = SSOClient()
        self.sso = sso
        self.api_version = api_version
        self.client = httpx.Client(base_url=base_url)
        self.access_token = None
        self.refresh_token = None

    def reauthenticate(self) -> None:
        try:
            logger.info("Refreshing token...")
            tokens = self.sso.refresh_token(self.refresh_token or "")
            self.access_token = tokens["access_token"]
        except httpx.HTTPStatusError:
            logger.info("Refresh failed, re-authenticating...")
            tokens = self.sso.fetch_tokens(self.username, self.password, self.otp)
            self.access_token = tokens["access_token"]
            self.refresh_token = tokens["refresh_token"]

    def json(self, path: str) -> dict:
        logger.info("Fetching %s...", path)
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-ION-API-VERSION": f"{self.api_version}",
        }
        res = self.client.get(path, headers=headers)
        try:
            res.raise_for_status()
        except httpx.HTTPStatusError:
            self.reauthenticate()
            headers["Authorization"] = f"Bearer {self.access_token}"
            res = self.client.get(path, headers=headers)
            res.raise_for_status()
        return res.json()
