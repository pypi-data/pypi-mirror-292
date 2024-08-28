from enum import Enum

from pydantic import BaseModel, ConfigDict


class Root(BaseModel):
    model_config = ConfigDict(extra="allow")

    messages: dict[str, list[str]]


class User(BaseModel):
    id: int
    username: str
    email: str
    is_staff: bool = False
    is_superuser: bool = False
    is_verified: bool = False
    is_authenticated: bool = True
    groups: list[int]


class Accessibility(str, Enum):
    PUBLIC = "PUBLIC"
    GATED = "GATED"
    PRIVATE = "PRIVATE"


class PermittedGroup(BaseModel):
    id: int
    name: str
    user_count: int


class ServiceInstance(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None = None
    management_group: int
    access_group: int

    permitted_groups: list[PermittedGroup]

    is_mutable: bool
    is_viewable: bool

    accessibility: Accessibility


class Ixmp4Instance(ServiceInstance):
    url: str
    dsn: str
    notice: str | None = None
