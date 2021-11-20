from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from appeals.repository.appeal_user_repository import IAppealUserRepository, AppealUserRepository
from appeals.repository.user_appeal_repository import UserAppealRepository, IUserAppealRepository
from common.service import BaseService
from users.models import User
from users.repository.departments_repository import IDepartmentRepository, DepartmentRepository


class IUserService(BaseService, ABC):
    @abstractmethod
    async def connect_to_all_appeals(self, creator_id: int, user: User):
        raise NotImplementedError


class UserService(IUserService):
    user_appeal_repos: IUserAppealRepository
    appeal_users_repos: IAppealUserRepository
    department_repos: IDepartmentRepository

    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.user_appeal_repos = UserAppealRepository(db=self.db)
        self.appeal_users_repos = AppealUserRepository(db=self.db)
        self.department_repos = DepartmentRepository(db=self.db)

    async def connect_to_all_appeals(self, creator_id: int, user: User):
        user_appeals_ids = await self.appeal_users_repos.get_user_appeals_ids(user_id=user.id)
        appeals_ids = await self.user_appeal_repos.get_all_ids_for_connect_employee(
            exclude_appeals_ids=user_appeals_ids)
        await self.appeal_users_repos.connect_user_to_appeals(creator_id=creator_id,
                                                              user_id=user.id,
                                                              exists_appeals_ids=appeals_ids)
