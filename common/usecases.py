from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession


class BaseUseCase(ABC):
    db: AsyncSession

    def __init__(self, db: AsyncSession):
        self.db = db