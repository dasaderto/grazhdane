import random
from random import choice

from faker import Faker
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from users.models import User, SexTypes, SocialGroup, UserRoles, Department
from users.repository.departments_repository import IDepartmentRepository, DepartmentRepository
from users.repository.social_groups_repository import SocialGroupRepository, ISocialGroupRepository


class SocialGroupSeeder:
    faker = Faker()
    repository: ISocialGroupRepository

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = SocialGroupRepository(db=db)

    async def seed(self) -> SocialGroup:
        social_group = SocialGroup()
        social_group.name = self.faker.word()
        social_group.is_active = True

        return social_group

    async def random_or_seed(self) -> SocialGroup:
        social_groups = await self.repository.get_all()
        if social_groups:
            return next(iter(social_groups))

        social_group = await self.seed()
        return social_group


class UserSeeder:
    faker = Faker()

    def __init__(self, db: AsyncSession):
        self.db = db

    async def seed(self) -> User:
        social_group = await SocialGroupSeeder(db=self.db).random_or_seed()

        user = User()
        user.first_name = self.faker.first_name()
        user.last_name = self.faker.last_name()
        user.patronymic = self.faker.first_name()
        user.email = self.faker.email()
        user.email_verified_at = None
        user.phone = self.faker.phone_number()
        user.sex = choice(list(SexTypes))
        user.position = self.faker.word()
        user.password = CryptContext(schemes=["bcrypt"], deprecated="auto").hash(self.faker.word() * 2)
        user.activate_token = None
        user.is_active = True
        user.social_group = social_group
        user.roles = [random.choice(list(UserRoles))]
        user.notify_active = True
        user.birthday = self.faker.past_datetime()
        user.address = self.faker.address()

        self.db.add(social_group)
        return user


class DepartmentSeeder:
    faker = Faker()
    department_repository: IDepartmentRepository

    def __init__(self, db: AsyncSession):
        self.db = db
        self.department_repository = DepartmentRepository(db=self.db)

    async def random_or_seed(self) -> Department:
        departments = await self.department_repository.get_all()
        if departments:
            return random.choice(departments)

        return await self.seed()

    async def seed(self) -> Department:
        director = await UserSeeder(db=self.db).seed()
        control = await UserSeeder(db=self.db).seed()

        department = Department()
        department.name = self.faker.word()
        department.director = director
        department.control = control

        self.db.add(director)
        self.db.add(control)

        return department
