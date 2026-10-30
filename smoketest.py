"""Run an end-to-end SDK smoke test against a running CrydenSync API."""

import json
import sys
import time

from crydensync import Cryden, CrydenError, MemoryStorageAdapter


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python smoketest.py <base-url>", file=sys.stderr)
        return 2

    client = Cryden(sys.argv[1], storage=MemoryStorageAdapter())
    email = "sdk-smoketest-{}@example.com".format(time.time_ns())
    password = "SmokeTestPass123!"

    def check(label, action):
        action()
        print("OK   " + label)

    def signup():
        if not client.sign_up(email, password).get("user_id"):
            raise AssertionError("signup response did not contain user_id")

    def duplicate_signup():
        try:
            client.sign_up(email, password)
        except CrydenError as error:
            if error.code != "user_exists":
                raise AssertionError("expected user_exists, got " + error.code)
        else:
            raise AssertionError("duplicate signup unexpectedly succeeded")

    def login():
        tokens = client.login(email, password)
        if not tokens.get("accessToken") or not tokens.get("refreshToken"):
            raise AssertionError("login response did not contain both tokens")

    def wrong_password():
        try:
            client.login(email, "wrong-password")
        except CrydenError as error:
            if error.code != "invalid_credentials":
                raise AssertionError("expected invalid_credentials, got " + error.code)
        else:
            raise AssertionError("wrong password unexpectedly succeeded")

    def verify():
        if not client.verify().get("user_id"):
            raise AssertionError("verify response did not contain user_id")

    def refresh_retry():
        raw = client.storage.get("cryden_tokens")
        tokens = json.loads(raw)
        tokens["accessToken"] = "expired-access-token"
        client.storage.set("cryden_tokens", json.dumps(tokens))
        if not client.verify().get("user_id"):
            raise AssertionError("verify after refresh did not contain user_id")

    def sessions():
        result = client.list_sessions()
        if not isinstance(result, list) or not result:
            raise AssertionError("expected at least one active session")

    def change_password():
        client.change_password(password, "NewSmokeTestPass456!")
        if client.is_authenticated():
            raise AssertionError("tokens were not cleared after password change")

    checks = [
        ("signup", signup),
        ("duplicate signup error code", duplicate_signup),
        ("login", login),
        ("is_authenticated after login", lambda: _assert(client.is_authenticated())),
        ("wrong password error code", wrong_password),
        ("verify", verify),
        ("automatic refresh and retry", refresh_retry),
        ("list_sessions", sessions),
        ("change_password clears tokens", change_password),
    ]
    try:
        for label, action in checks:
            check(label, action)
    except Exception as error:
        print("FAIL: {}".format(error), file=sys.stderr)
        return 1
    print("ALL CHECKS PASSED")
    return 0


def _assert(value):
    if not value:
        raise AssertionError("expected true")


if __name__ == "__main__":
    raise SystemExit(main())
