from typing import List, Protocol, Optional

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import subqueryload
from sqlalchemy.sql import Select, Subquery

from appeals.models import UserAppeal, AppealStatus, AppealStatuses
from common.repository import BaseRepository


class IUserAppealRepository(Protocol):
    async def get_all(self, ) -> List[UserAppeal]:
        raise NotImplementedError

    async def get_all_ids_for_connect_employee(self, exclude_appeals_ids: List[int]) -> List[int]:
        raise NotImplementedError

    async def get_count_all(self) -> int:
        raise NotImplementedError

    async def get_by_id(self, pk: int,
                        raise_exception: bool = False,
                        fetch_relations: bool = False) -> Optional[UserAppeal]:
        raise NotImplementedError


class UserAppealRepository(BaseRepository, IUserAppealRepository):
    model = UserAppeal

    def __init__(self, db: AsyncSession):
        super().__init__(db=db)

    async def get_all_ids_for_connect_employee(self, exclude_appeals_ids: List[int]) -> List[int]:
        query = await self.exec_query(
            self.select(UserAppeal.id)
                .join(UserAppeal.status)
                .where(UserAppeal.id.notin_(exclude_appeals_ids),
                       AppealStatus.status_const.in_([AppealStatuses.MODERATION, AppealStatuses.CONSIDERATION])))
        return query.scalars().fetchall()

    async def get_all(self) -> List[UserAppeal]:
        query = await self.exec_query(self.select(UserAppeal))
        return query.scalars().fetchall()

    async def get_count_all(self) -> int:
        query = await self.exec_query(func.count(UserAppeal.id))
        return query.scalar()

    def get_relations(self) -> List[Subquery]:
        return [subqueryload(UserAppeal.attachments)]

    async def get_by_id(self, pk: int,
                        raise_exception: bool = False,
                        fetch_relations: bool = False) -> Optional[UserAppeal]:
        select_query: Select = self.select(UserAppeal).where(UserAppeal.id == pk)
        if fetch_relations:
            select_query = select_query.options(*self.get_relations())
        query = await self.exec_query(select_query)
        user_appeal = query.scalars().first()
        if not user_appeal and raise_exception:
            raise HTTPException(status_code=404, detail=f"Undefined appeal with {pk=}")

        return user_appeal
