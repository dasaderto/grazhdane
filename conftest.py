import asyncio
import os

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from grazhdane.app import app
from grazhdane.database import async_session
from users.models import User
from users.types import JwtData
from users.usecases import AuthUseCase


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db():
    async with async_session() as session:
        yield session


@pytest.fixture
async def async_client() -> AsyncClient:
    async with AsyncClient(app=app, base_url=os.environ.get("APP_URL")) as async_client:
        yield async_client


def authorize_client(db: AsyncSession, client: AsyncClient, user: User):
    client.headers = {
        "Authorization": f"Bearer {AuthUseCase(db=db).create_access_token(data=JwtData(user_id=user.id))}"
    }
