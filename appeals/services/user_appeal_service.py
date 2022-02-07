from typing import List

from appeals.models import UserAppeal, UserAppealAttachment
from common.service import BaseService, AttachmentStorage
from common.types import UploadedFileType


class UserAppealService(BaseService):
    async def store_appeal_attachments(self, user_appeal: UserAppeal, files: List[UploadedFileType]):
        file_attachments = []
        for file in files:
            attachments_storage = AttachmentStorage(file=file.file, filename=file.filename,
                                                    dir_name='appeals')
            link = await attachments_storage.store()

            new_attachment = UserAppealAttachment()
            new_attachment.user_appeal = user_appeal
            new_attachment.link = link
            new_attachment.meta = attachments_storage.file_type
            new_attachment.creator = user_appeal.creator
            new_attachment.name = attachments_storage.filename
            file_attachments.append(new_attachment)
        self.db.add_all(file_attachments)
        await self.db.flush()
