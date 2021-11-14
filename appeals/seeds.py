import random

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from appeals.models import UserAppeal, AppealTheme, AppealStatus, AppealStatuses
from appeals.repository.appeal_status_repository import IAppealStatusRepository, AppealStatusRepository
from appeals.repository.appeal_theme_repository import IAppealThemeRepository, AppealThemeRepository
from appeals.repository.user_appeal_repository import IUserAppealRepository, UserAppealRepository
from users.seeds import UserSeeder, DepartmentSeeder


class AppealThemeSeeder:
    faker = Faker()
    appeal_theme_repository: IAppealThemeRepository

    def __init__(self, db: AsyncSession):
        self.db = db
        self.appeal_theme_repository = AppealThemeRepository(db=self.db)

    async def seed(self) -> AppealTheme:
        department = await DepartmentSeeder(db=self.db).random_or_seed()

        new_theme = AppealTheme()
        new_theme.theme = self.faker.word()
        new_theme.department = department
        new_theme.is_hidden = random.choice([False, True])

        return new_theme

    async def random_or_seed(self):
        appeal_themes = await self.appeal_theme_repository.get_all()
        if appeal_themes:
            return random.choice(appeal_themes)

        return await self.seed()


class AppealStatusSeeder:
    db: AsyncSession
    repository: IAppealStatusRepository

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = AppealStatusRepository(db=self.db)

    async def seed(self) -> AppealStatus:
        status = AppealStatus()
        status.status_const = status.title = random.choice(list(AppealStatuses))
        return status

    async def random_or_seed(self) -> AppealStatus:
        statuses = await self.repository.get_all()
        if statuses:
            return random.choice(statuses)

        return await self.seed()


class UserAppealSeeder:
    faker = Faker()
    repository: IUserAppealRepository

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = UserAppealRepository(db=self.db)

    async def random_or_seed(self) -> UserAppeal:
        appeals = await self.repository.get_all()
        if appeals:
            return random.choice(appeals)

        return await self.seed()

    async def seed(self) -> UserAppeal:
        creator = await UserSeeder(db=self.db).seed()
        appeal_theme = await AppealThemeSeeder(db=self.db).random_or_seed()
        appeal_status = await AppealStatusSeeder(db=self.db).random_or_seed()

        appeal = UserAppeal()
        appeal.creator = creator
        appeal.appeal_theme = appeal_theme
        appeal.executor = None
        appeal.deputy = None
        appeal.status = appeal_status
        appeal.problem_body = " ".join(self.faker.sentences())
        appeal.address = self.faker.address()
        appeal.post_address = self.faker.address()
        appeal.note = self.faker.sentence()
        appeal.is_active = True
        appeal.rate = 0
        appeal.dispatcher_create = random.choice([True, False])
        appeal.is_hidden = False
        appeal.expired_at = None
        appeal.users_voted = []

        self.db.add(creator)
        self.db.add(appeal_theme)
        self.db.add(appeal_status)

        return appeal
