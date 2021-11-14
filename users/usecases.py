import os
from datetime import timedelta, datetime
from typing import Optional, Tuple, List

from fastapi import HTTPException
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, constr, EmailStr, validator
from sqlalchemy.ext.asyncio import AsyncSession

from appeals.repository.appeal_user_repository import IAppealUserRepository, AppealUserRepository
from common.usecases import BaseUseCase
from users.models import User, SexTypes, UserRoles, Department, Employee
from users.repository.departments_repository import IDepartmentRepository, DepartmentRepository
from users.repository.social_groups_repository import SocialGroupRepository
from users.repository.user_repository import IUserRepository, UserRepository
from users.services.user_service import UserService


class RegisterData(BaseModel):
    first_name: constr(max_length=55)
    last_name: constr(max_length=55)
    patronymic: constr(max_length=55)
    email: EmailStr
    phone: constr(min_length=11)
    sex: Optional[SexTypes]
    password: constr(min_length=8)
    password_confirmation: constr(min_length=8)
    social_group_id: int

    @validator('password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password_confirmation' in values and v != values['password_confirmation']:
            raise ValueError('passwords do not match')
        return v


class LoginData(BaseModel):
    email: EmailStr
    password: str


class AuthUseCase(BaseUseCase):
    repository: IUserRepository
    __pwd_context: CryptContext = None

    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.repository = UserRepository(db=self.db)

    @property
    def pwd_context(self):
        if self.__pwd_context:
            return self.__pwd_context

        self.__pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return self.__pwd_context

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    async def authenticate_user(self, email: str, password: str):
        user = await self.repository.get_by_email(email=email)
        if not user:
            return False
        if not self.verify_password(password, user.password):
            return False
        return user

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, os.environ.get("SECRET_KEY"), algorithm=os.environ.get("ALGORITHM"))
        return encoded_jwt

    async def register(self, data: RegisterData) -> Tuple[User, str]:
        db_user = await self.repository.get_by_email(email=data.email)
        if db_user:
            raise HTTPException(status_code=400, detail="User with current email already registered")

        social_group = await SocialGroupRepository(db=self.db).get_by_id(pk=data.social_group_id)
        if not social_group:
            raise HTTPException(status_code=404, detail=f"Undefined social_group with {data.social_group_id} pk")

        user = User()
        user.first_name = data.first_name
        user.last_name = data.last_name
        user.patronymic = data.patronymic
        user.email = data.email
        user.phone = data.phone
        user.sex = data.sex
        user.password = self.get_password_hash(data.password)
        user.social_group = social_group

        self.db.add(user)
        await self.db.commit()

        return user, self.create_access_token(data={"user_id": user.id},
                                              expires_delta=timedelta(
                                                  days=int(os.environ.get("ACCESS_TOKEN_EXPIRE_DAYS"))))

    async def login(self, data: LoginData) -> Tuple[User, str]:
        user = await self.authenticate_user(email=data.email, password=data.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid user data")

        return user, self.create_access_token(data={"user_id": user.id},
                                              expires_delta=timedelta(
                                                  days=int(os.environ.get("ACCESS_TOKEN_EXPIRE_DAYS"))))


class CityHeadSetupData(BaseModel):
    email: EmailStr
    position: Optional[str]


class CityHeadSetupUC(BaseUseCase):
    repository: IUserRepository

    def __init__(self, db: AsyncSession, data: CityHeadSetupData):
        super().__init__(db)
        self.data = data
        self.repository = UserRepository(db=self.db)

    async def exec(self) -> User:
        user = await self.repository.get_by_email(email=self.data.email, raise_exception=True)
        old_users = await self.repository.get_by_role(role=UserRoles.CITY_HEAD_ROLE)
        for u in old_users:
            u.remove_role(UserRoles.CITY_HEAD_ROLE)
        user.assign_role(UserRoles.CITY_HEAD_ROLE)
        user.position = self.data.position

        await self.db.flush()

        return user


class AddControlUserData(BaseModel):
    email: EmailStr
    position: str


class AddControlUserUC(BaseUseCase):
    repository: IUserRepository

    def __init__(self, db: AsyncSession, data: AddControlUserData):
        super().__init__(db)
        self.data = data
        self.repository = UserRepository(self.db)

    async def exec(self) -> User:
        user = await self.repository.get_by_email(self.data.email, raise_exception=True)
        user.assign_role(role=UserRoles.CONTROL_ROLE)
        user.position = self.data.position
        await self.db.flush()

        return user


class AddEmployeeUserData(BaseModel):
    email: EmailStr
    position: str
    department_id: int
    is_director: bool


class AddEmployeeUserUC(BaseUseCase):
    repository: IUserRepository
    departments_repository = IDepartmentRepository

    def __init__(self, db: AsyncSession, data: AddEmployeeUserData):
        super().__init__(db)
        self.data = data
        self.repository = UserRepository(self.db)
        self.departments_repository = DepartmentRepository(self.db)

    def _create_employee(self, user: User, department: Department) -> Employee:
        employee = Employee()
        employee.user = user
        employee.department = department
        employee.position = self.data.position
        self.db.add(employee)

        return employee

    async def exec(self) -> User:
        user = await self.repository.get_by_email(email=self.data.email, raise_exception=True)
        user.position = self.data.position

        department = await self.departments_repository.get_by_id(pk=self.data.department_id)

        if self.data.is_director:
            user.assign_role(UserRoles.DEPARTMENT_HEAD_ROLE)
            department.director = user
        else:
            user.assign_role(UserRoles.EMPLOYEE_ROLE)
            self._create_employee(user=user, department=department)

        await self.db.flush()

        return user


class UpdateAdminUserData(BaseModel):
    user_id: int
    roles: List[UserRoles]
    first_name: str
    last_name: str
    patronymic: str
    phone: str
    social_group_id: int
    is_active: bool


class UpdateAdminUserUC(BaseUseCase):
    repository: IUserRepository
    appeal_user_repos: IAppealUserRepository
    service: UserService

    _user: User = None
    _is_old_admin = None

    def __init__(self, db: AsyncSession, auth_user_id: int, data: UpdateAdminUserData):
        super().__init__(db)
        self.auth_user_id = auth_user_id
        self.data = data
        self.repository = UserRepository(db=self.db)
        self.appeal_user_repos = AppealUserRepository(db=self.db)
        self.service = UserService(db=self.db)

    async def get_user(self) -> User:
        if not self._user:
            self._user = await self.repository.get_by_id(pk=self.data.user_id)
            self._is_old_admin = self._user.has_any_role(roles=[UserRoles.ADMIN_ROLE, UserRoles.MODERATOR_ROLE])
        return self._user

    async def _setup_roles(self):
        user = await self.get_user()
        old_roles = list(
            {UserRoles.EMPLOYEE_ROLE, UserRoles.DEPARTMENT_HEAD_ROLE, UserRoles.CONTROL_ROLE} & set(user.roles)
        )

        if not self.data.roles and not old_roles:
            user.assign_role(UserRoles.SIMPLE_USER_ROLE)
        else:
            user.roles = self.data.roles + old_roles

    async def _setup_appeal_connections(self):
        user = await self.get_user()
        if {UserRoles.ADMIN_ROLE, UserRoles.MODERATOR_ROLE} & set(self.data.roles):
            await self.service.connect_to_all_appeals(user=user, creator_id=self.auth_user_id)
        elif self._is_old_admin:
            await self.appeal_user_repos.disconnect_from_appeals(user_id=user.id)

    async def _update_user_data(self):
        user = await self.get_user()
        social_group = await SocialGroupRepository(db=self.db) \
            .get_by_id(pk=self.data.social_group_id, raise_exception=True)
        user.first_name = self.data.first_name
        user.last_name = self.data.last_name
        user.patronymic = self.data.patronymic
        user.phone = self.data.phone
        user.social_group = social_group
        user.is_active = self.data.is_active

    async def exec(self) -> User:
        await self._setup_roles()
        await self._setup_appeal_connections()
        await self._update_user_data()

        await self.db.flush()
        return await self.get_user()
