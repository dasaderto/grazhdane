from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class UserAppealEntity(BaseModel):
    creator_id: int
    appeal_theme_id: int
    executor_id: Optional[int]
    deputy_id: Optional[int]
    status_id: int

    problem_body: Optional[str]
    address: Optional[str]
    post_address: Optional[str]
    note: Optional[str]
    is_active: bool = False
    rate: int = 0
    dispatcher_create: Optional[int]
    is_hidden: bool = False
    expired_at: Optional[datetime]
    users_voted: Optional[List[int]]

    class Config:
        orm_mode = True
