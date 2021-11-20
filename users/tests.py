import os

import pytest
from faker import Faker
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from appeals.models import AppealStatus, AppealStatuses
from appeals.repository.appeal_user_repository import AppealUserRepository
from appeals.repository.user_appeal_repository import UserAppealRepository
from appeals.seeds import UserAppealSeeder
from conftest import authorize_client
from grazhdane import config
from users.models import UserRoles, User
from users.repository.departments_repository import DepartmentRepository
from users.repository.employee_repository import EmployeeRepository
from users.repository.user_repository import UserRepository
from users.seeds import UserSeeder, DepartmentSeeder, SocialGroupSeeder
from users.usecases import (
    CityHeadSetupUC, CityHeadSetupData, AddControlUserUC, AddControlUserData,
    AddEmployeeUserData, AddEmployeeUserUC, UpdateAdminUserData, UpdateAdminUserUC, ActivateUserUC,
)

pytestmark = pytest.mark.asyncio


async def test_city_head_setup_uc(db: AsyncSession):
    user_repos = UserRepository(db=db)

    new_city_head_user = await UserSeeder(db).seed()
    old_city_head_user = await UserSeeder(db).seed()

    new_city_head_user.roles = [UserRoles.SIMPLE_USER_ROLE]
    old_city_head_user.roles = [UserRoles.CITY_HEAD_ROLE]

    db.add(new_city_head_user)
    db.add(old_city_head_user)
    await db.commit()

    new_city_head = await CityHeadSetupUC(db=db, data=CityHeadSetupData(
        email=new_city_head_user.email,
        position=Faker().word(),
    )).exec()

    new_city_head_user = await user_repos.get_by_id(pk=new_city_head_user.id)
    old_city_head_user = await user_repos.get_by_id(pk=old_city_head_user.id)

    assert old_city_head_user
    assert new_city_head_user
    assert UserRoles.CITY_HEAD_ROLE in new_city_head.roles
    assert UserRoles.CITY_HEAD_ROLE not in old_city_head_user.roles
    assert UserRoles.CITY_HEAD_ROLE in new_city_head_user.roles


async def test_add_control_user(db: AsyncSession):
    new_control_user = await UserSeeder(db).seed()

    db.add(new_control_user)
    await db.commit()

    await AddControlUserUC(db=db, data=AddControlUserData(
        email=new_control_user.email,
        position=Faker().word(),
    )).exec()

    control_user = await UserRepository(db=db).get_by_id(pk=new_control_user.id)

    assert control_user
    assert UserRoles.CONTROL_ROLE in control_user.roles


async def test_add_department_director_user(db: AsyncSession):
    new_director = await UserSeeder(db).seed()
    department = await DepartmentSeeder(db).seed()

    db.add(new_director)
    db.add(department)
    await db.commit()

    data = AddEmployeeUserData(
        email=new_director.email,
        position=Faker().word(),
        department_id=department.id,
        is_director=True,
    )

    user: User = await AddEmployeeUserUC(db=db, data=data).exec()
    new_director = await UserRepository(db=db).get_by_id(pk=new_director.id)
    new_department = await DepartmentRepository(db=db).get_by_id(pk=department.id, raise_exception=True)

    assert UserRoles.DEPARTMENT_HEAD_ROLE in user.roles
    assert UserRoles.DEPARTMENT_HEAD_ROLE in new_director.roles
    assert new_department.director_id == new_director.id


async def test_add_department_employee_user(db: AsyncSession):
    new_user = await UserSeeder(db).seed()
    department = await DepartmentSeeder(db).seed()

    db.add(new_user)
    db.add(department)
    await db.commit()

    data = AddEmployeeUserData(
        email=new_user.email,
        position=Faker().word(),
        department_id=department.id,
        is_director=False,
    )

    user: User = await AddEmployeeUserUC(db=db, data=data).exec()
    new_employee = await UserRepository(db=db).get_by_id(pk=new_user.id)
    employee = await EmployeeRepository(db=db).get_by_user_id(user_id=user.id)
    assert UserRoles.EMPLOYEE_ROLE in user.roles
    assert UserRoles.EMPLOYEE_ROLE in new_employee.roles
    assert employee
    assert employee.user_id == user.id


async def test_update_admin_user(db: AsyncSession):
    new_user = await UserSeeder(db=db).seed()
    new_user.roles = [UserRoles.EMPLOYEE_ROLE]

    social_group = await SocialGroupSeeder(db=db).seed()

    auth_user = await UserSeeder(db=db).seed()
    appeals = [await UserAppealSeeder(db=db).random_or_seed(), await UserAppealSeeder(db=db).random_or_seed()]
    appeals[0].status = AppealStatus(title=AppealStatuses.MODERATION, status_const=AppealStatuses.MODERATION)
    appeals[1].status = AppealStatus(title=AppealStatuses.CONSIDERATION, status_const=AppealStatuses.CONSIDERATION)

    db.add_all(appeals)
    db.add(new_user)
    db.add(social_group)
    db.add(auth_user)
    await db.commit()
    faker = Faker()
    data = UpdateAdminUserData(
        user_id=new_user.id,
        roles=[UserRoles.ADMIN_ROLE],
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        patronymic=faker.first_name(),
        phone=faker.phone_number(),
        social_group_id=social_group.id,
        is_active=True,
    )

    await UpdateAdminUserUC(auth_user_id=auth_user.id, data=data, db=db).exec()
    user_appeal_repository = UserAppealRepository(db=db)
    appeal_user_repository = AppealUserRepository(db=db)
    updated_new_user = await UserRepository(db=db).get_by_id(pk=new_user.id)

    assert updated_new_user.roles == [UserRoles.ADMIN_ROLE, UserRoles.EMPLOYEE_ROLE]

    all_appeal_ids = await user_appeal_repository.get_all_ids_for_connect_employee(exclude_appeals_ids=[])
    user_appeals_ids = await appeal_user_repository.get_user_appeals_ids(user_id=new_user.id)
    assert len(all_appeal_ids) == len(user_appeals_ids)

    updated_user = await UserRepository(db=db).get_by_id(pk=new_user.id)
    assert data.first_name == updated_user.first_name
    assert data.last_name == updated_user.last_name
    assert data.patronymic == updated_user.patronymic
    assert data.phone == updated_user.phone
    assert data.is_active == updated_user.is_active
    assert data.social_group_id == updated_user.social_group_id


async def test_avatar_update(db: AsyncSession, async_client: AsyncClient):
    user = await UserSeeder(db=db).seed()
    db.add(user)
    await db.commit()
    print(user.id)
    authorize_client(db=db, client=async_client, user=user)
    files = [
        ('file', ('foo.png', open(os.path.join(config.MEDIA_ROOT, 'ZiClJf-1920w.jpeg'), 'rb'), 'image/jpeg'))
    ]
    response: Response = await async_client.post("/users/update-avatar", files=files)
    assert response.status_code == 200
    response_data = response.json()
    file_url = response_data.get('data').replace("/media/", "")
    filepath = os.path.join(config.MEDIA_ROOT, file_url)
    assert os.path.isfile(filepath)
    db_user = await UserRepository(db=db).get_by_id(pk=user.id)
    assert db_user.avatar == response_data.get('data')
    os.remove(filepath)


async def test_user_activation(db: AsyncSession):
    user = await UserSeeder(db=db).seed()
    db.add(user)
    await db.commit()

    await ActivateUserUC(db=db, user_id=user.id, is_activated=False).exec()
    db_user = await UserRepository(db).get_by_id(pk=user.id)
    assert not db_user.is_active

    await ActivateUserUC(db=db, user_id=user.id, is_activated=True).exec()
    db_user = await UserRepository(db).get_by_id(pk=user.id)
    assert db_user.is_active
