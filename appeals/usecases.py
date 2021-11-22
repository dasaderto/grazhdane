from typing import List, Union, Optional

from fastapi import Form
from pydantic import BaseModel, constr, validator
from sqlalchemy.ext.asyncio import AsyncSession

from appeals.models import AppealStatuses, UserAppeal, UserAppealAttachment, AppealUser
from appeals.repository.appeal_history_repository import IAppealHistoryRepository, AppealHistoryRepository
from appeals.repository.appeal_status_repository import IAppealStatusRepository, AppealStatusRepository
from appeals.repository.appeal_theme_repository import IAppealThemeRepository, AppealThemeRepository
from common.errors import ValidationError
from common.service import AttachmentStorage
from common.types import UploadedFileType
from common.usecases import BaseUseCase
from postgis.point import Point
from users.models import User


class CreateUserAppealData(BaseModel):
    appeal_theme_id: int
    problem_body: constr(max_length=700)
    address: str
    locate: List[Union[float, int]]
    is_active: Optional[bool]

    @classmethod
    def as_form(cls,
                appeal_theme_id: int = Form(...),
                address: str = Form(...),
                locate: str = Form(...),
                is_active: Optional[bool] = Form(...),
                problem_body: constr(max_length=700) = Form(...)):
        locate = list(map(float, locate.split(",")))
        return cls(
            appeal_theme_id=appeal_theme_id,
            problem_body=problem_body,
            address=address,
            locate=locate,
            is_active=is_active,
        )

    @validator("locate")
    def validate_locate(cls, locate: List[Union[float, int]]):
        if len(locate) != 2:
            raise ValidationError(detail={"locate": "Locate must be coords"})
        return locate


class CreateUserAppealUC(BaseUseCase):
    status_repos: IAppealStatusRepository
    appeal_theme_repos: IAppealThemeRepository
    appeal_history_repos: IAppealHistoryRepository

    def __init__(self, db: AsyncSession,
                 ctx_user: User,
                 data: CreateUserAppealData,
                 files: List[UploadedFileType]):
        super().__init__(db)
        self.data = data
        self.files = files
        self.ctx_user = ctx_user
        self.status_repos = AppealStatusRepository(db=self.db)
        self.appeal_theme_repos = AppealThemeRepository(db=self.db)
        self.appeal_history_repos = AppealHistoryRepository(db=self.db)

    async def create_appeal(self) -> UserAppeal:
        status = await self.status_repos.get_by_const_name(const_name=AppealStatuses.MODERATION)
        appeal_theme = await self.appeal_theme_repos.get_by_id(pk=self.data.appeal_theme_id, raise_exception=True)

        new_appeal = UserAppeal()
        new_appeal.appeal_theme = appeal_theme
        new_appeal.status = status
        new_appeal.problem_body = self.data.problem_body
        new_appeal.address = self.data.address
        new_appeal.is_active = self.data.is_active
        new_appeal.creator = self.ctx_user

        lat, lng = self.data.locate
        new_appeal.locate = Point(lat=lat, lng=lng).to_wkt()

        self.db.add(new_appeal)
        await self.db.flush()
        return new_appeal

    async def store_attachments(self, appeal: UserAppeal):
        file_attachments = []
        if self.files:
            for file in self.files:
                attachments_storage = AttachmentStorage(file=file.file, filename=file.filename,
                                                        dir_name='appeals')
                link = await attachments_storage.store()

                new_attachment = UserAppealAttachment()
                new_attachment.user_appeal = appeal
                new_attachment.link = link
                new_attachment.meta = attachments_storage.file_type
                new_attachment.creator = self.ctx_user
                new_attachment.name = attachments_storage.filename
                file_attachments.append(new_attachment)
        self.db.add_all(file_attachments)
        await self.db.flush()

    async def create_appeal_user(self, appeal: UserAppeal) -> AppealUser:
        appeal_user = AppealUser()
        appeal_user.appeal = appeal

        self.db.add(appeal_user)
        await self.db.flush()
        return appeal_user

    async def exec(self) -> UserAppeal:
        try:
            new_appeal = await self.create_appeal()
            await self.store_attachments(appeal=new_appeal)
            await self.appeal_history_repos.create_moderation_message(appeal=new_appeal)
            await self.create_appeal_user(appeal=new_appeal)
        except Exception as e:
            await self.db.rollback()
            raise e

        await self.db.commit()
        return new_appeal
