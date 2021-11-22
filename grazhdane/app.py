import logging

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi_pagination import add_pagination

from grazhdane.router import main_router

load_dotenv()
logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(main_router)
add_pagination(app)

APPLICATIONS = [
    'common',
    'users',
    'polls',
    'appeals',
    'gis',
    'initiatives',
]
