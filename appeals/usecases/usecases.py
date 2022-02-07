from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from appeals.models import AppealStatuses, UserAppeal, AppealUser, AppealTheme
from appeals.repository.appeal_attachment_repository import IAppealAttachmentRepository, AppealAttachmentRepository
from appeals.repository.appeal_history_repository import IAppealHistoryRepository, AppealHistoryRepository
from appeals.repository.appeal_status_repository import IAppealStatusRepository, AppealStatusRepository
from appeals.repository.appeal_theme_repository import IAppealThemeRepository, AppealThemeRepository
from appeals.repository.user_appeal_repository import IUserAppealRepository, UserAppealRepository
from appeals.services.user_appeal_service import UserAppealService
from appeals.usecases.types import UserAppealData, MoveAppealToWorkData
from common.types import UploadedFileType
from common.usecases import BaseUseCase
from postgis.point import Point
from users.models import User, Department
from users.repository.user_repository import IUserRepository, UserRepository


class CreateUserAppealUC(BaseUseCase):
    status_repos: IAppealStatusRepository
    appeal_theme_repos: IAppealThemeRepository
    appeal_history_repos: IAppealHistoryRepository
    user_appeal_service: UserAppealService

    def __init__(self, db: AsyncSession, ctx_user: User, data: UserAppealData, files: List[UploadedFileType]):
        super().__init__(db)
        self.data = data
        self.files = files
        self.ctx_user = ctx_user
        self.status_repos = AppealStatusRepository(db=self.db)
        self.appeal_theme_repos = AppealThemeRepository(db=self.db)
        self.appeal_history_repos = AppealHistoryRepository(db=self.db)
        self.user_appeal_service = UserAppealService(db=self.db)

    async def _create_appeal(self) -> UserAppeal:
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

    async def _store_attachments(self, appeal: UserAppeal):
        if self.files:
            await self.user_appeal_service.store_appeal_attachments(user_appeal=appeal, files=self.files)

    async def _create_appeal_user(self, appeal: UserAppeal) -> AppealUser:
        appeal_user = AppealUser()
        appeal_user.appeal = appeal

        self.db.add(appeal_user)
        await self.db.flush()
        return appeal_user

    async def exec(self) -> UserAppeal:
        try:
            new_appeal = await self._create_appeal()
            await self._store_attachments(appeal=new_appeal)
            await self.appeal_history_repos.create_moderation_message(appeal=new_appeal)
            await self._create_appeal_user(appeal=new_appeal)
        except Exception as e:
            await self.db.rollback()
            raise e

        await self.db.commit()
        return new_appeal


class UpdateUserAppealUC(BaseUseCase):
    appeal_attachment_repos: IAppealAttachmentRepository
    appeal_theme_repos: IAppealThemeRepository
    user_appeal_service: UserAppealService

    def __init__(self, db: AsyncSession, user_appeal: UserAppeal, data: UserAppealData, files: List[UploadedFileType]):
        super().__init__(db)
        self.user_appeal = user_appeal
        self.data = data
        self.files = files

        self.appeal_attachment_repos = AppealAttachmentRepository(db=self.db)
        self.appeal_theme_repos = AppealThemeRepository(db=self.db)
        self.user_appeal_service = UserAppealService(db=self.db)

    async def _recreate_attachments(self):
        if not self.files:
            return

        await self.appeal_attachment_repos.delete_by_appeal_id(appeal_id=self.user_appeal.id)
        await self.user_appeal_service.store_appeal_attachments(user_appeal=self.user_appeal, files=self.files)

    async def _process_update(self):
        appeal_theme = await self.appeal_theme_repos.get_by_id(pk=self.data.appeal_theme_id, raise_exception=True)

        self.user_appeal.appeal_theme = appeal_theme
        self.user_appeal.problem_body = self.data.problem_body
        self.user_appeal.address = self.data.address
        self.user_appeal.is_active = self.data.is_active
        await self.db.flush()

    async def exec(self):
        await self._recreate_attachments()
        await self._process_update()
        await self.db.commit()


class MoveAppealToWorkUC(BaseUseCase):
    _appeal_theme: AppealTheme = None
    _department: Department = None
    appeal_theme_repos: IAppealThemeRepository
    user_repos: IUserRepository
    appeal_repos: IUserAppealRepository

    def __init__(self, db: AsyncSession, data: MoveAppealToWorkData):
        super().__init__(db)
        self.data = data
        self.appeal_theme_repos = AppealThemeRepository(db=db)
        self.user_repos = UserRepository(db=db)
        self.appeal_repos = UserAppealRepository(db=db)

    async def _process_update(self):
        appeal_theme = await self.appeal_theme_repos.get_by_id(pk=self.data.appeal_theme_id, raise_exception=True)
        dept_director = await self.user_repos.get_department_director(department_id=appeal_theme.department_id)
        user_appeal = await self.appeal_repos.get_by_id(pk=self.data.appeal_id, raise_exception=True)
        user_appeal.executor = dept_director
        user_appeal.appeal_theme = appeal_theme
        user_appeal.is_active = self.data.is_active
        user_appeal.note = self.data.note
        # ['deputyId', 'appealThemeId', 'isActive', 'note']

    async def exec(self):
        await self._process_update()
