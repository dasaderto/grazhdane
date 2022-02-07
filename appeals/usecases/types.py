from fastapi import Form
from pydantic import BaseModel, constr, validator
from typing import List, Union, Optional

from common.errors import ValidationError
from common.types import UploadedFileType


class UserAppealData(BaseModel):
    appeal_theme_id: int
    problem_body: constr(max_length=700)
    address: str
    locate: List[Union[float, int]]
    is_active: Optional[bool]

    @classmethod
    def as_form(cls,
                appeal_theme_id: int = Form(...),
                address: str = Form(...),
                locate: str = Form(...),
                is_active: Optional[bool] = Form(...),
                problem_body: constr(max_length=700) = Form(...)):
        locate = list(map(float, locate.split(",")))
        return cls(
            appeal_theme_id=appeal_theme_id,
            problem_body=problem_body,
            address=address,
            locate=locate,
            is_active=is_active,
        )

    @validator("locate")
    def validate_locate(cls, locate: List[Union[float, int]]):
        if len(locate) != 2:
            raise ValidationError(detail={"locate": "Locate must be coords"})
        return locate


class MoveAppealToWorkData(BaseModel):
    appeal_id: int
    note: Optional[str]
    appeal_theme_id: int
    deputy_id: Optional[int]
    is_active: Optional[bool]
