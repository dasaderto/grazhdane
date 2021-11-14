from abc import ABC
from typing import Union

from sqlalchemy import select
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select, Delete


class BaseRepository(ABC):
    db: AsyncSession

    def __init__(self, db: AsyncSession):
        self.db = db

    async def exec_query(self, query: Union[Select, Delete]) -> ChunkedIteratorResult:
        return await self.db.execute(query)

    def select(self, *args) -> Select:
        return select(*args)
