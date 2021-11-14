from abc import abstractmethod
from typing import Protocol, List

from sqlalchemy import select, delete
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.sql import Select, Delete

from appeals.models import AppealUser
from common.repository import BaseRepository


class IAppealUserRepository(Protocol):
    @abstractmethod
    async def get_user_appeals_ids(self, user_id: int) -> List[int]:
        raise NotImplementedError

    @abstractmethod
    async def connect_user_to_appeals(self, creator_id: int, user_id: int, exists_appeals_ids: List[int]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def disconnect_from_appeals(self, user_id: int) -> int:
        raise NotImplementedError


class AppealUserRepository(BaseRepository, IAppealUserRepository):
    model = AppealUser

    async def get_user_appeals_ids(self, user_id: int) -> List[int]:
        select_query: Select = select(self.model.appeal_id)
        query: ChunkedIteratorResult = await self.db.execute(select_query.where(AppealUser.employee_id == user_id))
        return query.fetchall()

    async def connect_user_to_appeals(self, creator_id: int, user_id: int, exists_appeals_ids: List[int]) -> None:
        new_connections = []
        for appeal_id in exists_appeals_ids:
            new_connection: AppealUser = AppealUser()
            new_connection.appeal_id = appeal_id
            new_connection.employee_id = user_id
            new_connection.creator_id = creator_id
            new_connection.is_private = False

            new_connections.append(new_connection)
            if len(new_connections) == 30:
                self.db.add_all(new_connections)
                await self.db.flush()
                new_connections = []
        else:
            self.db.add_all(new_connections)
            await self.db.flush()

    async def disconnect_from_appeals(self, user_id: int) -> int:
        delete_query: Delete = delete(AppealUser)
        return await self.db.execute(delete_query.where(AppealUser.employee_id == user_id))
