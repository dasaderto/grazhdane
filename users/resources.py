from pydantic import BaseModel

from users.entities import UserEntity


class AuthUserOut(BaseModel):
    user: UserEntity
    access_token: str
    token_type: str


class AuthUserOutResource(BaseModel):
    data: AuthUserOut


class UserOutResource(BaseModel):
    data: UserEntity
