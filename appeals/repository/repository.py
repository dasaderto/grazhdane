from typing import List, Protocol

from sqlalchemy import select, Column
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from appeals.models import UserAppeal, AppealStatus, AppealStatuses


class IUserAppealRepository(Protocol):
    async def get_all_ids_for_connect_employee(self, exclude_appeals_ids: List[int]) -> List[int]:
        raise NotImplementedError


class UserAppealRepository(IUserAppealRepository):
    model = UserAppeal

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_ids_for_connect_employee(self, exclude_appeals_ids: List[int]) -> List[int]:
        select_func: Select = select(UserAppeal.id)
        query: ChunkedIteratorResult = await self.db.execute(
            select_func
                .join(UserAppeal.status)
                .where(UserAppeal.id.notin_(exclude_appeals_ids),
                       AppealStatus.status_const.in_([AppealStatuses.MODERATION, AppealStatuses.CONSIDERATION])))

        return query.scalars().fetchall()