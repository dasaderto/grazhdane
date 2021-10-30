from dotenv import load_dotenv
from fastapi import FastAPI

from users.handlers import users_router

load_dotenv()

app = FastAPI()
app.include_router(users_router)

APPLICATIONS = [
    'common',
    'users',
    'polls',
    'appeals',
    'gis',
    'initiatives',
]
