import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from grazhdane.app import app
from users.departments_repository import DepartmentRepository
from users.employee_repository import EmployeeRepository
from users.models import UserRoles, User
from users.repository import UserRepository
from users.seeds import UserSeeder, DepartmentSeeder
from users.usecases import CityHeadSetupUC, CityHeadSetupData, AddControlUserUC, AddControlUserData, \
    AddEmployeeUserData, AddEmployeeUserUC

client = TestClient(app)

pytestmark = pytest.mark.asyncio


async def test_city_head_setup_uc(db: AsyncSession):
    user_repos = UserRepository(db=db)

    new_city_head_user = await UserSeeder(db).seed()
    old_city_head_user = await UserSeeder(db).seed()

    new_city_head_user.roles = [UserRoles.SIMPLE_USER_ROLE]
    old_city_head_user.roles = [UserRoles.CITY_HEAD_ROLE]

    db.add(new_city_head_user)
    db.add(old_city_head_user)
    await db.flush()

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
    await db.flush()

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
    await db.flush()

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
    await db.flush()

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
