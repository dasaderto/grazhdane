import logging

from dotenv import load_dotenv
from fastapi import FastAPI

from grazhdane.router import main_router

load_dotenv()
logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(main_router)

APPLICATIONS = [
    'common',
    'users',
    'polls',
    'appeals',
    'gis',
    'initiatives',
]
