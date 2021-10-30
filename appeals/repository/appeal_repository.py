from sqlalchemy.ext.asyncio import AsyncSession

from appeals.models import AppealUser


class AppealUserRepository:
    model = AppealUser

    def __init__(self, db: AsyncSession):
        self.db = db