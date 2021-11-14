from typing import List, Protocol

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from appeals.models import UserAppeal, AppealStatus, AppealStatuses
from common.repository import BaseRepository


class IUserAppealRepository(Protocol):
    async def get_all(self, ) -> List[UserAppeal]:
        raise NotImplementedError

    async def get_all_ids_for_connect_employee(self, exclude_appeals_ids: List[int]) -> List[int]:
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

    async def get_count_all(self):
        query = await self.exec_query(func.count(UserAppeal.id))
        return query.scalar()
