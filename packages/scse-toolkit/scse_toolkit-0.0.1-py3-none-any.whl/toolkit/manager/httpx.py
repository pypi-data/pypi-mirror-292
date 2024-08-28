import logging

import httpx

from toolkit.exceptions import InvalidCredentials
from toolkit.manager import ManagerClient

from ..token import PreencodedToken, create_token, decode, encode

logger = logging.getLogger(__file__)


class Auth(httpx.Auth):
    def __str__(self):
        return f"<{self.__class__.__name__}>"


class SelfSignedAuth(Auth):
    """Generates its own JWT with the supplied secret."""

    def __init__(
        self,
        secret: str,
        issuer: str = "scse-toolkit",
        username: str = "@self-signed",
    ):
        self.secret = secret
        self.token = create_token(username, issuer)

    def auth_flow(self, r):
        r.headers["Authorization"] = "Bearer " + encode(
            self.token, self.secret, refresh=True
        )
        yield r


class ManagerAuth(Auth):
    """Uses the SceSe Management Service to obtain and refresh a token."""

    refresh_token: PreencodedToken
    access_token: PreencodedToken

    def __init__(
        self,
        username: str,
        password: str,
        url: str,
    ):
        self.client = httpx.Client(base_url=url, http2=True)
        self.username = username
        self.password = password
        self.obtain_jwt()

    def auth_flow(self, r):
        if self.access_token.is_expired():
            self.refresh_or_reobtain_jwt()

        r.headers["Authorization"] = "Bearer " + self.access_token.encoded_str
        yield r

    def obtain_jwt(self):
        res = self.client.post(
            "/token/obtain/",
            json={
                "username": self.username,
                "password": self.password,
            },
        )
        if res.status_code >= 400:
            if res.status_code == 401:
                raise InvalidCredentials()
            else:
                res.raise_for_status()

        json = res.json()
        self.access_token = decode(json["access"])
        self.refresh_token = decode(json["refresh"])

    def refresh_or_reobtain_jwt(self):
        if self.refresh_token.is_expired():
            self.obtain_jwt()
        else:
            self.refresh_jwt()

    def refresh_jwt(self):
        res = self.client.post(
            "/token/refresh/",
            json={
                "refresh": self.refresh_token.encoded_str,
            },
        )
        res.raise_for_status()
        self.access_token = decode(res.json()["access"])


class ImpersonatingAuth(ManagerAuth):
    def __init__(
        self,
        url: str,
        secret: str,
        user_id: int,
    ):
        self.admin_client = ManagerClient(url, SelfSignedAuth(secret))
        self.user_id = user_id
        self.obtain_jwt()

    def obtain_jwt(self):
        json = self.admin_client.users.impersonate(self.user_id)
        self.access_token = decode(json["access"])
        self.refresh_token = decode(json["refresh"])
