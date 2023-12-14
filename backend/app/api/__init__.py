from fastapi import APIRouter

from app.api import release
from app.api import utils
from app.api import discogs

api_router = APIRouter()

api_router.include_router(utils.router, tags=["utils"])
api_router.include_router(release.router, tags=["release"])
api_router.include_router(discogs.router, tags=["discogs"])