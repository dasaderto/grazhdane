import sqlalchemy
from sqlalchemy import Column, DateTime, func, Integer, String

from grazhdane.database import Base


class BaseORMModel(Base):
    __abstract__ = True

    id: Column = sqlalchemy.Column(Integer, primary_key=True, index=True)


class TimeStampedModel(BaseORMModel):
    __abstract__ = True

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime)
