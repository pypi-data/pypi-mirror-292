import json
import logging
from collections.abc import Iterable
from typing import Generic, TypeVar

import httpx
from pydantic import BaseModel

from .models import Ixmp4Instance, Root, User

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=BaseModel)


class ModelRepository(Generic[ModelType]):
    response_model: type[ModelType]
    prefix: str
    client: httpx.Client

    def __init__(
        self, client: httpx.Client, prefix: str, response_model: type[ModelType]
    ) -> None:
        self.client = client
        self.prefix = prefix
        self.response_model = response_model

        if not self.prefix.endswith("/"):
            self.prefix += "/"

    def normalize_params(self, params: dict) -> dict[str, str]:
        """Encodes list parameters as comma-seperated strings because
        httpx does not have a way to customize this behaviour."""

        for key, val in params.items():
            if isinstance(val, Iterable):
                list_ = list(json.dumps(i) for i in val)
                params[key] = ",".join(list_)
        return params

    def list(self, **kwargs) -> list[ModelType]:
        """Retrieves a list of objects."""
        logger.debug(f"Listing `{self.response_model.__name__}` objects...")
        res = self.client.get(
            self.prefix,
            params=self.normalize_params({"page_size": -1, **kwargs}),
        )
        res.raise_for_status()
        json = res.json()
        return [self.response_model(**r) for r in json.get("results", [])]

    def retrieve(self, id: int) -> ModelType:
        """Retrieves an object with the supplied id."""
        logger.debug(f"Retrieving `{self.response_model.__name__}` object...")
        res = self.client.get(self.prefix + str(id) + "/")
        res.raise_for_status()
        return self.response_model(**res.json())


class UserRepository(ModelRepository[User]):
    def __init__(self, client: httpx.Client) -> None:
        super().__init__(client, "users/", User)

    def impersonate(self, id: int) -> dict[str, str]:
        """Retrieves new authentication tokens for the
        user with the supplied id. Only works if
        a `superuser` authentication token is set."""

        res = self.client.get(self.prefix + str(id) + "/impersonate/")
        res.raise_for_status()
        return res.json()

    def me(self):
        """Retrieves the current user if an authentication
        token is set."""

        res = self.client.get(self.prefix + "me/")
        res.raise_for_status()
        return self.response_model(**res.json())


class ManagerClient(object):
    def __init__(
        self, url: str, auth: httpx.Auth | None = None, timeout: int = 10
    ) -> None:
        logger.debug(
            f"Connecting to manager instance at '{url}' using "
            f"auth class `{auth}`..."
        )
        self.url = url
        self.auth = auth
        self.client = httpx.Client(
            base_url=self.url,
            timeout=timeout,
            http2=True,
            auth=auth,
            follow_redirects=True,
        )

        self.check_root()

        self.ixmp4 = ModelRepository(self.client, "ixmp4/", Ixmp4Instance)
        self.users = UserRepository(self.client)

    def check_root(self):
        """Requests root api endpoint and logs messages."""
        res = self.client.get("/")
        res.raise_for_status()
        root = Root(**res.json())

        for warning in root.messages.get("warning", []):
            logger.warn(warning)

        for info in root.messages.get("info", []):
            logger.info(info)
