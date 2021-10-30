from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, constr, EmailStr


class UserEntity(BaseModel):
    id: int
    first_name: constr(max_length=150)
    last_name: Optional[constr(max_length=150)]
    patronymic: Optional[constr(max_length=150)]
    email: EmailStr
    email_verified_at: Optional[datetime]
    phone: Optional[constr(max_length=50)]
    sex: str
    position: Optional[str]
    activate_token: Optional[str]
    is_active: bool
    social_group_id: int
    roles: List[str] = list
    notify_active: bool
    birthday: Optional[datetime]
    address: Optional[str]

    class Config:
        orm_mode = True
