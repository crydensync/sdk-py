"""Typed response models returned by the CrydenSync API."""

from typing import TypedDict


class Tokens(TypedDict):
    access_token: str
    refresh_token: str


class SignUpResult(TypedDict):
    user_id: str
    email: str


class Session(TypedDict, total=False):
    id: str
    ip: str
    user_agent: str
    created_at: str
