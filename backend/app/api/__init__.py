from fastapi import APIRouter

from app.api import utils,playbook

api_router = APIRouter()

api_router.include_router(utils.router, tags=["utils"])
api_router.include_router(playbook.router, tags=["playbook"])