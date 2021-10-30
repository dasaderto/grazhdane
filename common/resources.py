from pydantic import BaseModel


class BaseResource(BaseModel):
    data: BaseModel
