from enum import Enum
from pydantic import BaseModel


class TokenLogin(BaseModel):
    token: str
    login: str


class TokenLoginId(TokenLogin):
    login_id: int


class Action(str, Enum):
    Update = "update"
    New = "new"
    Delete = "delete"


class TokenLoginAction(TokenLogin):
    action: Action