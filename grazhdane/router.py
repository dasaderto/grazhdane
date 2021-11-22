from fastapi import APIRouter

from appeals.handlers.user_appeal_handlers import user_appeals_router
from users.handlers import users_router

main_router = APIRouter()
main_router.include_router(users_router, prefix="/users", tags=["users"])
main_router.include_router(user_appeals_router, prefix="/appeals", tags=["appeals"])
