from fastapi_pagination.default import Page
from sqlalchemy import Column
from typing import TypeVar, Generic, List

from grazhdane.models import BaseORMModel

T = TypeVar("T")


class JsonApiPage(Page[T], Generic[T]):
    """JSON:API 1.0 specification says that result key should be a `data`."""

    class Config:
        allow_population_by_field_name = True
        fields = {"items": {"alias": "data"}, "size": {"alias": "per_page"}}


class SetupModelAttributes:
    def __init__(self, instance: BaseORMModel, data: dict, fields: List[Column] = ()):
        self.instance = instance
        self.data = data
        self.fields = fields

    def process(self):
        fields_names = [field.name for field in self.fields]
        for field_name, val in self.data.items():
            if self.fields and field_name not in fields_names:
                continue
            setattr(self.instance, field_name, self.data.get(field_name, getattr(self.instance, field_name)))
