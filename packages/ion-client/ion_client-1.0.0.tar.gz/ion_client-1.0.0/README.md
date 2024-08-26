# ion-client
[![Tests](https://img.shields.io/github/actions/workflow/status/maxmouchet/ion-client/tests.yml?logo=github)](https://github.com/maxmouchet/ion-client/actions/workflows/tests.yml)
[![PyPI](https://img.shields.io/pypi/v/ion-client?logo=pypi&logoColor=white)](https://pypi.org/project/ion-client/)

Simple Aruba Instant On client. Handles re-authentication and 2FA with one-time passwords.

## Installation

```bash
pip install ion-client
```

## Usage

```python
from ion_client import Client

# Omit `otp` to login without 2FA
client = Client("user@example.org", "password", "otp")

sites = client.json("/sites")
# {"elements": [{'kind': 'site', 'id': '...', 'name': '...', ...}]}

client.json(f"/sites/{sites[0]['id']}/clientSummary")
# {"elements": [{'kind': 'wirelessClientSummary', 'id': '...', 'name': '...', ...}]}
```
