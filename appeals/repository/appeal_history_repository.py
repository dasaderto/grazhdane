from typing import Optional

from fastapi import HTTPException

from appeals.models import AppealHistory, UserAppeal, AppealHistoryTypes
from common.repository import BaseRepository


class IAppealHistoryRepository(BaseRepository):
    model = AppealHistory

    async def create_moderation_message(self, appeal: UserAppeal) -> AppealHistory:
        raise NotImplementedError

    async def get_by_id(self, pk: int, raise_exception: bool = False) -> Optional[AppealHistory]:
        raise NotImplementedError

    async def get_by_appeal_type(self, appeal_id: int, history_type: AppealHistoryTypes) -> Optional[AppealHistory]:
        raise NotImplementedError


class AppealHistoryRepository(IAppealHistoryRepository):
    model = AppealHistory

    async def create_moderation_message(self, appeal: UserAppeal) -> AppealHistory:
        comment = f"Сообщение № {appeal.id} было отправлено на модерацию"
        history = AppealHistory()
        history.appeal = appeal
        history.creator = appeal.creator
        history.comment = comment
        history.type = AppealHistoryTypes.APPEAL_MODERATION

        self.db.add(history)
        await self.db.flush()
        return history

    async def get_by_id(self, pk: int, raise_exception: bool = False) -> Optional[AppealHistory]:
        query = await self.exec_query(self.select(self.model).where(self.model.id == pk))
        history = query.scalars().first()

        if not history and raise_exception:
            raise HTTPException(status_code=404, detail=f"Undefined history with {pk=}")

        return history

    async def get_by_appeal_type(self, appeal_id: int, history_type: AppealHistoryTypes) -> Optional[AppealHistory]:
        query = await self.exec_query(self.select(self.model).where(self.model.appeal_id == appeal_id,
                                                                    self.model.type == history_type))

        return query.scalars().first()
