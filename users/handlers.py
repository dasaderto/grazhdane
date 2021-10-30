from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer
from fastapi_utils.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession

from grazhdane.database import get_async_db
from users.entities import UserEntity
from users.resources import AuthUserOutResource, UserOutResource
from users.usecases import AuthUseCase, RegisterData, LoginData, CityHeadSetupUC, CityHeadSetupData, AddControlUserData, \
    AddControlUserUC, AddEmployeeUserData, AddEmployeeUserUC

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

users_router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@cbv(users_router)
class UserHandler:
    db: AsyncSession = Depends(get_async_db)

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
    async def set_city_head(self, data: CityHeadSetupData):
        user = await CityHeadSetupUC(db=self.db, data=data).exec()

        return {
            'data': UserEntity.from_orm(user)
        }

    @users_router.post("/add/control-user", response_model=UserOutResource)
    async def add_control_user(self, data: AddControlUserData):
        user = await AddControlUserUC(db=self.db, data=data).exec()

        return {
            'data': UserEntity.from_orm(user)
        }

    @users_router.post("/add/employee-user", response_model=UserOutResource)
    async def add_employee_user(self, data: AddEmployeeUserData):
        user = await AddEmployeeUserUC(db=self.db, data=data).exec()

        return {
            'data': UserEntity.from_orm(user)
        }