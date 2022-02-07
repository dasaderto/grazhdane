from abc import abstractmethod
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Protocol, Optional, List, Iterable

from common.repository import BaseRepository
from users.models import User, UserRoles, Department


class IUserRepository(Protocol):
    @abstractmethod
    async def get_all(self) -> List[User]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, pk: int, raise_exception: bool = False) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str, raise_exception: bool = False) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_role(self, role: UserRoles) -> Optional[Iterable[User]]:
        raise NotImplementedError

    @abstractmethod
    async def get_department_director(self, department_id: int) -> User:
        raise NotImplementedError


class UserRepository(BaseRepository, IUserRepository):
    model = User

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_by_id(self, pk: int, raise_exception: bool = False) -> Optional[User]:
        query = await self.exec_query(self.select(self.model).where(User.id == pk))
        user = query.scalars().first()
        if not user and raise_exception:
            raise HTTPException(status_code=404, detail=f"Undefined user with {pk=}")
        return user

    async def get_by_email(self, email: str, raise_exception: bool = False) -> Optional[User]:
        query = await self.exec_query(self.select(self.model).where(User.email == email))
        user = query.scalars().first()
        if not user and raise_exception:
            raise HTTPException(status_code=404, detail=f"Undefined user with email {email}")
        return user

    async def get_all(self) -> List[User]:
        query = await self.exec_query(self.select(self.model))
        return query.scalars().fetchall()

    async def get_by_role(self, role: UserRoles) -> Optional[Iterable[User]]:
        query = await self.exec_query(self.select(self.model).where(User.roles.contains([role])))
        return query.scalars().fetchall()

    async def get_department_director(self, department_id: int) -> User:
        select_query = self.select(self.model) \
            .join(Department, onclause=User.id == Department.director_id) \
            .where(Department.id == department_id)
        query = await self.exec_query(select_query)
        return query.scalars().first()
