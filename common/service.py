from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession


class BaseService(ABC):
    db: AsyncSession

    def __init__(self, db: AsyncSession):
        self.db = db
