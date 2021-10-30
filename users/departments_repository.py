from abc import abstractmethod
from typing import Protocol, Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from users.models import Department


class IDepartmentRepository(Protocol):
    @abstractmethod
    async def get_by_id(self, pk: int, raise_exception: bool = False) -> Optional[Department]:
        raise NotImplementedError


class DepartmentRepository(IDepartmentRepository):
    model = Department

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, pk: int, raise_exception: bool = False) -> Optional[Department]:
        select_query: Select = select(Department)
        query: ChunkedIteratorResult = await self.db.execute(select_query.where(Department.id == pk))
        department = query.scalars().first()
        if not department and raise_exception:
            raise HTTPException(status_code=404, detail=f"Undefined department with pk {pk}")
        return department
