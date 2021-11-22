from abc import abstractmethod
from typing import Protocol, List, Optional

from fastapi import HTTPException

from appeals.models import AppealStatus
from common.repository import BaseRepository


class IAppealStatusRepository(Protocol):
    @abstractmethod
    async def get_all(self) -> List[AppealStatus]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_const_name(self, const_name: str, raise_exception: bool = False) -> Optional[AppealStatus]:
        raise NotImplementedError


class AppealStatusRepository(BaseRepository, IAppealStatusRepository):
    model = AppealStatus

    async def get_all(self) -> List[AppealStatus]:
        query = await self.exec_query(self.select(AppealStatus))
        return query.scalars().fetchall()

    async def get_by_const_name(self, const_name: str, raise_exception: bool = False) -> Optional[AppealStatus]:
        query = await self.exec_query(self.select(AppealStatus).where(AppealStatus.status_const == const_name))
        status = query.scalars().first()
        if not status and raise_exception:
            raise HTTPException(status_code=404, detail=f"Undefined status with {const_name=}")
        return status
