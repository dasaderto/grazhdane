from abc import abstractmethod
from typing import Protocol, Optional, List, Iterable

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from users.models import User, UserRoles


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


class UserRepository(IUserRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, pk: int, raise_exception: bool = False) -> Optional[User]:
        query: ChunkedIteratorResult = await self.db.execute(select(User).where(User.id == pk))
        user = query.scalars().first()
        if not user and raise_exception:
            raise HTTPException(status_code=404, detail=f"Undefined user with {pk=}")
        return user

    async def get_by_email(self, email: str, raise_exception: bool = False) -> Optional[User]:
        query: ChunkedIteratorResult = await self.db.execute(select(User).where(User.email == email))
        user = query.scalars().first()
        if not user and raise_exception:
            raise HTTPException(status_code=404, detail=f"Undefined user with email {email}")
        return user

    async def get_all(self) -> List[User]:
        query: ChunkedIteratorResult = await self.db.execute(select(User))
        return query.scalars().fetchall()

    async def get_by_role(self, role: UserRoles) -> Optional[Iterable[User]]:
        select_users: Select = select(User)
        query: ChunkedIteratorResult = await self.db.execute(select_users.where(User.roles.contains([role])))
        return query.scalars().fetchall()
