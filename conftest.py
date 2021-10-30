import asyncio

import pytest

from grazhdane.database import async_session


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db():
    async with async_session() as session:
        yield session
