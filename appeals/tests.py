import os
import random

import pytest
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from appeals.models import AppealHistoryTypes
from appeals.repository.appeal_history_repository import AppealHistoryRepository
from appeals.repository.appeal_user_repository import AppealUserRepository
from appeals.repository.user_appeal_repository import UserAppealRepository
from appeals.seeds import AppealThemeSeeder
from appeals.usecases import CreateUserAppealUC, CreateUserAppealData
from common.types import UploadedFileType
from grazhdane import config
from users.seeds import UserSeeder

pytestmark = pytest.mark.asyncio


async def test_create_user_appeal_uc(db: AsyncSession):
    user = await UserSeeder(db=db).seed()
    appeal_theme = await AppealThemeSeeder(db=db).random_or_seed()

    db.add(user)
    db.add(appeal_theme)
    await db.commit()

    faker = Faker()
    data = CreateUserAppealData(
        appeal_theme_id=appeal_theme.id,
        problem_body=faker.sentence(),
        address=faker.address(),
        locate=faker.latlng(),
        is_active=random.choice([True, False])
    )

    with open(os.path.join(config.MEDIA_ROOT, 'testfile.jpeg'), mode='rb') as f:
        files = [UploadedFileType(filename="testfile.jpeg", file=f)]
        new_appeal = await CreateUserAppealUC(db=db, ctx_user=user, data=data, files=files).exec()

        assert new_appeal
        db_appeal = await UserAppealRepository(db=db).get_by_id(pk=new_appeal.id, fetch_relations=True)
        assert len(db_appeal.attachments) == len(files)

        file_url = db_appeal.attachments[0].link.replace("/media/", "")
        filepath = os.path.join(config.MEDIA_ROOT, file_url)
        assert os.path.isfile(filepath)
        os.remove(filepath)

        appeal_history = await AppealHistoryRepository(db=db).get_by_appeal_type(
            appeal_id=db_appeal.id,
            history_type=AppealHistoryTypes.APPEAL_MODERATION)
        assert appeal_history is not None

        appeal_users = await AppealUserRepository(db=db).get_by_appeal_id(appeal_id=db_appeal.id)
        assert len(appeal_users) == 1
