from fastapi import APIRouter

from users.handlers import users_router

main_router = APIRouter()
main_router.include_router(users_router, prefix="/users", tags=["users"])
