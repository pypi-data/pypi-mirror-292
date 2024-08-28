import json
from datetime import datetime, timedelta
from enum import Enum
from functools import lru_cache
from uuid import uuid4

import jwt
from pydantic import BaseModel

from .manager.models import User

token_lifetime = timedelta(minutes=15)
token_algorithm = "HS256"


class TokenType(str, Enum):
    access = "access"
    refresh = "refresh"

    def __str__(self) -> str:
        return self.value


class Token(BaseModel):
    """Model used to serialize and validate the 'json' part of a JWT."""

    token_type: TokenType
    exp: int
    jti: str
    sub: str
    # TODO: The manager should return this.
    iss: str = "urn:iiasa:ece:scse-manager"
    user_id: int | None = None
    user: User | None = None

    @property
    def is_serviceaccount(self):
        return self.user_id is None

    def is_expired(self):
        return self.exp < datetime.now().timestamp()

    def __hash__(self):
        dump = self.model_dump(mode="json")
        return hash(json.dumps(dump, sort_keys=True))


class PreencodedToken(Token):
    encoded_str: str | None = None


@lru_cache
def cached_encode(token: Token, secret: str) -> str:
    return jwt.encode(
        token.model_dump(mode="json", exclude_unset=True),
        secret,
        algorithm=token_algorithm,
    )


def get_exp() -> int:
    return int((datetime.now() + token_lifetime).timestamp())


def create_token(
    sub: str, issuer: str, token_type: TokenType = TokenType.access
) -> Token:
    """Creates a new token with fresh uuid and expiration timestamp."""
    jti = uuid4().hex
    exp = get_exp()
    token = Token(
        token_type=token_type,
        exp=exp,
        jti=jti,
        sub=sub,
        iss=f"urn:iiasa:ece:{issuer}",
    )
    return token


def encode(token: Token, secret: str, refresh: bool = False) -> str:
    """Encodes the given token model into a header-ready string.
    If `refresh is `True` and the token has expired, it will be refreshed."""

    if refresh and token.is_expired():
        token.exp = get_exp()
    return cached_encode(token, secret)


def decode(token_str: str):
    """Decodes the given token string into a token model.
    Does not check the token for validity."""

    token_dict = jwt.decode(
        token_str,
        options={"verify_signature": False, "verify_exp": False},
        algorithm=token_algorithm,
    )
    return PreencodedToken(**token_dict, encoded_str=token_str)


def verify(token_str: str, secret: str):
    """Decodes the given token string into a token model
    and verifies expiration and signature."""

    token_dict = jwt.decode(token_str, secret, algorithm=token_algorithm)
    return PreencodedToken(**token_dict, encoded_str=token_str)
