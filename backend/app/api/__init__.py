from fastapi import APIRouter

from app.api import release
from app.api import utils

api_router = APIRouter()

api_router.include_router(utils.router, tags=["utils"])
api_router.include_router(release.router, tags=["release"])