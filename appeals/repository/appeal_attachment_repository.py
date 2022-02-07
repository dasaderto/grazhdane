from sqlalchemy import delete

from appeals.models import UserAppealAttachment
from common.repository import BaseRepository


class IAppealAttachmentRepository(BaseRepository):
    async def delete_by_appeal_id(self, appeal_id: int) -> int:
        raise NotImplementedError


class AppealAttachmentRepository(IAppealAttachmentRepository):
    model = UserAppealAttachment

    async def delete_by_appeal_id(self, appeal_id: int) -> int:
        query = await self.exec_query(delete(self.model).where(UserAppealAttachment.user_appeal_id == appeal_id))
        return query.scalars().fetchall()
