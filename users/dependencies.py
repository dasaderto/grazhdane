import os

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from grazhdane.database import get_async_db
from users.models import User, UserRoles
from users.repository.user_repository import UserRepository
from users.types import JwtData

security = HTTPBearer()


async def get_authenticated_user(credentials: HTTPAuthorizationCredentials = Depends(security),
                                 db: AsyncSession = Depends(get_async_db)):
    jwt_token = credentials.credentials
    try:
        decoded_jwt: JwtData = jwt.decode(jwt_token,
                                          key=os.environ.get("SECRET_KEY"),
                                          algorithms=os.environ.get("ALGORITHM"))
        user = await UserRepository(db=db).get_by_id(pk=decoded_jwt.get('user_id'))
        if not user:
            raise JWTError("Undefined user")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Unauthorized")


async def get_admin_authenticated_user(auth_user: User = Depends(get_authenticated_user)):
    if not auth_user.has_role(UserRoles.ADMIN_ROLE):
        raise HTTPException(status_code=403, detail="User has no admin role")

    return auth_user
