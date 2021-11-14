from abc import abstractmethod
from typing import Protocol, List

from appeals.models import AppealStatus
from common.repository import BaseRepository


class IAppealStatusRepository(Protocol):
    @abstractmethod
    async def get_all(self) -> List[AppealStatus]:
        raise NotImplementedError


class AppealStatusRepository(BaseRepository, IAppealStatusRepository):
    model = AppealStatus

    async def get_all(self) -> List[AppealStatus]:
        query = await self.exec_query(self.select(AppealStatus))
        return query.scalars().fetchall()
