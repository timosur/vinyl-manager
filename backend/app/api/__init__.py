from fastapi import APIRouter

from app.api import discogs, release, utils, backup, mixtape

api_router = APIRouter()

api_router.include_router(utils.router, tags=["utils"])
api_router.include_router(release.router, tags=["release"])
api_router.include_router(discogs.router, tags=["discogs"])
api_router.include_router(backup.router, tags=["backup"])
api_router.include_router(mixtape.router, tags=["mixtape"])
