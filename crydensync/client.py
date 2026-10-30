"""Synchronous client for the CrydenSync authentication API."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .errors import CrydenError, error_from_payload
from .storage import StorageAdapter, default_storage_adapter
from .types import Session, SignUpResult, Tokens

_TOKEN_STORAGE_KEY = "cryden_tokens"


class Cryden:
    """HTTP client with stored tokens and one automatic refresh retry.

    ``base_url`` is the API origin, for example ``https://auth.example.com``.
    The SDK adds the ``/v1`` route prefix itself. Tokens are kept in memory by
    default; pass a :class:`StorageAdapter` to customize persistence.
    """

    def __init__(self, base_url: str, storage: Optional[StorageAdapter] = None,
                 timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.storage = storage if storage is not None else default_storage_adapter()
        self.timeout = timeout

    def _tokens(self) -> Optional[Dict[str, str]]:
        raw = self.storage.get(_TOKEN_STORAGE_KEY)
        if not raw:
            return None
        try:
            value = json.loads(raw)
        except (TypeError, ValueError):
            return None
        if not isinstance(value, dict):
            return None
        access, refresh = value.get("accessToken"), value.get("refreshToken")
        if not isinstance(access, str) or not isinstance(refresh, str):
            return None
        return {"accessToken": access, "refreshToken": refresh}

    def _save_tokens(self, tokens: Dict[str, str]) -> None:
        self.storage.set(_TOKEN_STORAGE_KEY, json.dumps(tokens))

    def _clear_tokens(self) -> None:
        self.storage.remove(_TOKEN_STORAGE_KEY)

    def is_authenticated(self) -> bool:
        """Return whether a token pair is stored, without validating it."""
        return self._tokens() is not None

    def _raw_request(self, path: str, method: str,
                     body: Optional[object] = None,
                     access_token: Optional[str] = None
                     ) -> Tuple[int, Any]:
        headers = {"Content-Type": "application/json"}
        if access_token:
            headers["Authorization"] = "Bearer " + access_token
        data = None if body is None else json.dumps(body).encode("utf-8")
        request = Request(self.base_url + path, data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                status = response.status
                raw = response.read()
        except HTTPError as error:
            status = error.code
            raw = error.read()
        except (URLError, OSError) as error:
            raise CrydenError("network_error", "could not reach the server", 0) from error
        try:
            return status, json.loads(raw.decode("utf-8")) if raw else {}
        except (UnicodeDecodeError, ValueError):
            return status, {}

    @staticmethod
    def _raise_response_error(status: int, payload: Any) -> None:
        raise error_from_payload(status, payload)

    def _authed_request(self, path: str, method: str,
                        body: Optional[object] = None) -> Any:
        tokens = self._tokens()
        if tokens is None:
            raise CrydenError("invalid_access_token", "not authenticated", 401)
        status, payload = self._raw_request(path, method, body, tokens["accessToken"])
        if status == 401:
            refreshed = self._try_refresh()
            if refreshed is not None:
                status, payload = self._raw_request(path, method, body, refreshed["accessToken"])
        if status >= 400:
            self._raise_response_error(status, payload)
        return payload.get("data") if isinstance(payload, dict) else None

    def _try_refresh(self) -> Optional[Dict[str, str]]:
        tokens = self._tokens()
        if tokens is None:
            return None
        status, payload = self._raw_request(
            "/v1/refresh", "POST", {"refresh_token": tokens["refreshToken"]}
        )
        data = payload.get("data") if isinstance(payload, dict) else None
        if status >= 400 or not isinstance(data, dict):
            self._clear_tokens()
            return None
        fresh = {"accessToken": data.get("access_token"),
                 "refreshToken": data.get("refresh_token")}
        if not all(isinstance(value, str) and value for value in fresh.values()):
            self._clear_tokens()
            return None
        self._save_tokens(fresh)
        return fresh

    def sign_up(self, email: str, password: str) -> SignUpResult:
        status, payload = self._raw_request("/v1/signup", "POST",
                                            {"email": email, "password": password})
        if status >= 400:
            self._raise_response_error(status, payload)
        return payload.get("data", {})

    def login(self, email: str, password: str) -> Tokens:
        status, payload = self._raw_request("/v1/login", "POST",
                                            {"email": email, "password": password})
        if status >= 400:
            self._raise_response_error(status, payload)
        data = payload.get("data", {})
        tokens = {"accessToken": data.get("access_token"),
                  "refreshToken": data.get("refresh_token")}
        self._save_tokens(tokens)
        return tokens  # type: ignore[return-value]

    def logout(self, session_id: str) -> None:
        self._authed_request("/v1/logout", "POST", {"session_id": session_id})
        self._clear_tokens()

    def logout_all(self) -> None:
        self._authed_request("/v1/logout-all", "POST")
        self._clear_tokens()

    def verify(self) -> Dict[str, str]:
        return self._authed_request("/v1/verify", "GET")

    def list_sessions(self) -> list[Session]:
        return self._authed_request("/v1/sessions", "GET")

    def revoke_session(self, session_id: str) -> None:
        self._authed_request("/v1/sessions/" + session_id, "DELETE")

    def change_password(self, current_password: str, new_password: str) -> None:
        self._authed_request("/v1/change-password", "POST", {
            "current_password": current_password,
            "new_password": new_password,
        })
        self._clear_tokens()

    def delete_account(self, current_password: str) -> None:
        self._authed_request("/v1/delete-account", "POST",
                             {"current_password": current_password})
        self._clear_tokens()

    def request_email_change(self, new_email: str) -> None:
        self._authed_request("/v1/email/request-change", "POST",
                             {"new_email": new_email})

    def confirm_email_change(self, token: str) -> None:
        status, payload = self._raw_request("/v1/email/confirm-change", "POST",
                                            {"token": token})
        if status >= 400:
            self._raise_response_error(status, payload)
