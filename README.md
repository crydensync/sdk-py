# CrydenSync Python SDK

A synchronous, dependency-free Python client for the authentication API. Its
supported methods match the current `@crydensync/sdk` JavaScript client.

## Install

```bash
pip install crydensync-sdk
```

For local development:

```bash
pip install -e .
```

## Usage

```python
from crydensync import Cryden, CrydenError

client = Cryden("https://auth.example.com")
user = client.sign_up("dev@example.com", "SecurePass123!")
tokens = client.login("dev@example.com", "SecurePass123!")
print(user["user_id"], client.verify()["user_id"])

try:
    sessions = client.list_sessions()
except CrydenError as error:
    print(error.code, error.status, str(error))
```

The SDK adds `/v1` to the base URL. It stores tokens in memory by default.
Supply a storage adapter to customize persistence:

```python
from crydensync import Cryden, FileStorageAdapter

client = Cryden(
    "https://auth.example.com",
    storage=FileStorageAdapter("~/.config/myapp/cryden-tokens.json"),
)
```

`FileStorageAdapter` stores its values as plain text. Choose an encrypted
adapter when local filesystem access is not trusted. You can also implement
`StorageAdapter` with `get(key)`, `set(key, value)`, and `remove(key)` methods.

## Supported methods

- `sign_up`, `login`, `is_authenticated`
- `logout`, `logout_all`, `verify`
- `list_sessions`, `revoke_session`
- `change_password`, `delete_account`
- `request_email_change`, `confirm_email_change`

Authenticated calls refresh once after a 401 and retry with the new access
token. Failed refresh clears the stored token pair. Password changes and
account deletion clear local tokens after success. Email change confirmation
does not require authentication.

## Development

```bash
python -m pip install -e .
python smoketest.py http://localhost:8080
```

## License

MIT
