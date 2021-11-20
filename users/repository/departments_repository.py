from abc import abstractmethod
from typing import Protocol, Optional, List

from fastapi import HTTPException

from common.repository import BaseRepository
from users.models import Department


class IDepartmentRepository(Protocol):
    @abstractmethod
    async def get_by_id(self, pk: int, raise_exception: bool = False) -> Optional[Department]:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> List[Department]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_director_id(self, director_id: int) -> Optional[Department]:
        raise NotImplementedError


class DepartmentRepository(BaseRepository, IDepartmentRepository):
    model = Department

    async def get_by_id(self, pk: int, raise_exception: bool = False) -> Optional[Department]:
        query = await self.exec_query(self.select(Department).where(Department.id == pk))
        department = query.scalars().first()
        if not department and raise_exception:
            raise HTTPException(status_code=404, detail=f"Undefined department with pk {pk}")
        return department

    async def get_all(self) -> List[Department]:
        query = await self.exec_query(self.select(Department))
        return query.scalars().fetchall()

    async def get_by_director_id(self, director_id: int) -> Optional[Department]:
        query = await self.exec_query(self.select(Department).where(Department.director_id == director_id))
        return query.scalars().first()
