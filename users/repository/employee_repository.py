from abc import abstractmethod
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from users.models import Employee


class IEmployeeRepository(Protocol):
    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> Employee:
        raise NotImplementedError


class EmployeeRepository(IEmployeeRepository):
    model = Employee

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: int) -> Employee:
        select_query: Select = select(Employee)
        query: ChunkedIteratorResult = await self.db.execute(select_query.where(Employee.user_id == user_id))
        return query.scalars().first()