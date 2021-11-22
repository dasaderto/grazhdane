import logging
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi_pagination import paginate
from fastapi_utils.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession

from appeals.entities import UserAppealEntity
from appeals.repository.user_appeal_repository import UserAppealRepository
from appeals.resourses import UserAppealOutResource
from appeals.usecases import CreateUserAppealData, CreateUserAppealUC
from common.types import UploadedFileType
from common.utils import JsonApiPage
from grazhdane.database import get_async_db
from users.dependencies import get_authenticated_user
from users.models import User

user_appeals_router = APIRouter()


@cbv(user_appeals_router)
class UserHandler:
    db: AsyncSession = Depends(get_async_db)
    logger = logging.getLogger(__name__)

    @user_appeals_router.get("/", response_model=JsonApiPage[UserAppealEntity])
    async def appeals_list(self):
        appeals = await UserAppealRepository(db=self.db).get_all()
        return paginate([UserAppealEntity.from_orm(appeal) for appeal in appeals])

    @user_appeals_router.post("/create", response_model=UserAppealOutResource)
    async def create(self,
                     data: CreateUserAppealData = Depends(CreateUserAppealData.as_form),
                     files: List[UploadFile] = File(...),
                     auth_user: User = Depends(get_authenticated_user)):
        prepared_files = [UploadedFileType(file=f.file, filename=f.filename) for f in files]
        new_appeal = await CreateUserAppealUC(db=self.db, ctx_user=auth_user, data=data, files=prepared_files).exec()

        return UserAppealOutResource(data=UserAppealEntity.from_orm(new_appeal))
