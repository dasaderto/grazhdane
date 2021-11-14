from abc import abstractmethod
from typing import Protocol, List

from appeals.models import AppealTheme
from common.repository import BaseRepository


class IAppealThemeRepository(Protocol):
    @abstractmethod
    async def get_all(self) -> List[AppealTheme]:
        raise NotImplementedError


class AppealThemeRepository(BaseRepository, IAppealThemeRepository):
    model = AppealTheme

    async def get_all(self) -> List[AppealTheme]:
        query = await self.exec_query(self.select(self.model))
        return query.scalars().fetchall()
