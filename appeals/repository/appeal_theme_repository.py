from abc import abstractmethod
from typing import Protocol, List, Optional

from fastapi import HTTPException

from appeals.models import AppealTheme
from common.repository import BaseRepository


class IAppealThemeRepository(Protocol):
    @abstractmethod
    async def get_all(self) -> List[AppealTheme]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, pk: int, raise_exception: bool = False) -> Optional[AppealTheme]:
        raise NotImplementedError


class AppealThemeRepository(BaseRepository, IAppealThemeRepository):
    model = AppealTheme

    async def get_all(self) -> List[AppealTheme]:
        query = await self.exec_query(self.select(self.model))
        return query.scalars().fetchall()

    async def get_by_id(self, pk: int, raise_exception: bool = False) -> Optional[AppealTheme]:
        query = await self.exec_query(self.select(self.model).where(AppealTheme.id == pk))
        appeal_theme = query.scalars().first()
        if not appeal_theme and raise_exception:
            raise HTTPException(status_code=404, detail=f"Undefined appeal_theme with {pk=}")
        return appeal_theme
