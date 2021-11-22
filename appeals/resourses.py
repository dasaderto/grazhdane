from pydantic import BaseModel

from appeals.entities import UserAppealEntity


class UserAppealOutResource(BaseModel):
    data: UserAppealEntity
