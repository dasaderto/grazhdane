import logging

from fastapi import Depends, APIRouter, UploadFile, File
from fastapi_utils.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession

from grazhdane.database import get_async_db
from users.dependencies import get_authenticated_user, get_auth_dependency
from users.entities import UserEntity
from users.models import UserRoles
from users.resources import AuthUserOutResource, UserOutResource
from users.usecases import (
    AuthUseCase, RegisterData, LoginData, CityHeadSetupUC, CityHeadSetupData, AddControlUserData,
    AddControlUserUC, AddEmployeeUserData, AddEmployeeUserUC, UpdateUserAvatarUC, UpdateUserAvatarData, ActivateUserUC,
)

users_router = APIRouter()


@cbv(users_router)
class UserHandler:
    db: AsyncSession = Depends(get_async_db)
    logger = logging.getLogger(__name__)

    @users_router.post("/register", response_model=AuthUserOutResource)
    async def register_user(self, data: RegisterData):
        user, token = await AuthUseCase(db=self.db).register(data=data)

        return {
            "data": {
                "user": UserEntity.from_orm(user),
                "access_token": token,
                "token_type": 'Bearer',
            }
        }

    @users_router.post("/login", response_model=AuthUserOutResource)
    async def login_user(self, data: LoginData):
        user, token = await AuthUseCase(db=self.db).login(data=data)

        return {
            "data": {
                "user": UserEntity.from_orm(user),
                "access_token": token,
                "token_type": 'Bearer',
            }
        }

    @users_router.post("/set/city-head", response_model=UserOutResource)
    async def set_city_head(self, data: CityHeadSetupData, admin_user=get_auth_dependency([UserRoles.ADMIN_ROLE])):
        user = await CityHeadSetupUC(db=self.db, data=data).exec()

        return {
            'data': UserEntity.from_orm(user)
        }

    @users_router.post("/add/control-user", response_model=UserOutResource)
    async def add_control_user(self, data: AddControlUserData, admin_user=get_auth_dependency([UserRoles.ADMIN_ROLE])):
        user = await AddControlUserUC(db=self.db, data=data).exec()

        return {
            'data': UserEntity.from_orm(user)
        }

    @users_router.post("/add/employee-user", response_model=UserOutResource)
    async def add_employee_user(self, data: AddEmployeeUserData,
                                admin_user=get_auth_dependency([UserRoles.ADMIN_ROLE])):
        user = await AddEmployeeUserUC(db=self.db, data=data).exec()

        return {
            'data': UserEntity.from_orm(user)
        }

    @users_router.post("/set/employee-user", response_model=UserOutResource)
    async def set_employee_user(self, data: AddEmployeeUserData,
                                admin_user=get_auth_dependency([UserRoles.ADMIN_ROLE])):
        user = await AddEmployeeUserUC(db=self.db, data=data).exec()

        return {
            'data': UserEntity.from_orm(user)
        }

    @users_router.post("/update-avatar")
    async def avatar_update(self, auth_user=Depends(get_authenticated_user), file: UploadFile = File(...)):
        data = UpdateUserAvatarData(file=file.file.read(), filename=file.filename)
        user = await UpdateUserAvatarUC(db=self.db, user=auth_user, data=data).exec()

        return {
            "data": user.avatar
        }

    @users_router.post("/activate/user/{user_id}/{is_activated}", response_model=UserOutResource)
    async def user_activate(self, user_id: int, is_activated: int,
                            auth_user=get_auth_dependency([UserRoles.ADMIN_ROLE, UserRoles.MODERATOR_ROLE])):
        user = await ActivateUserUC(db=self.db, user_id=user_id, is_activated=bool(is_activated)).exec()

        return {
            'data': UserEntity.from_orm(user)
        }
