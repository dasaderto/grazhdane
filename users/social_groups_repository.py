from abc import abstractmethod
from typing import Protocol, Optional, List, Iterable

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from users.models import SocialGroup


class ISocialGroupRepository(Protocol):
    @abstractmethod
    async def get_by_id(self, pk: int, raise_exception: bool = False) -> Optional[SocialGroup]:
        raise NotImplementedError


class SocialGroupRepository(ISocialGroupRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, pk: int, raise_exception: bool = False) -> Optional[SocialGroup]:
        select_func: Select = select(SocialGroup)
        query: ChunkedIteratorResult = await self.db.execute(select_func.where(SocialGroup.id == pk))
        social_group = query.scalars().first()
        if not social_group and raise_exception:
            raise HTTPException(status_code=404, detail=f"Undefined social group with id {pk}")
        return social_group

    async def get_all(self) -> Iterable[SocialGroup]:
        query: ChunkedIteratorResult = await self.db.execute(select(SocialGroup))
        return query.scalars().fetchall()