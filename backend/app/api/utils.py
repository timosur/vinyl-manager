from typing import Any

from fastapi import APIRouter

from app.schemas.msg import Msg

router = APIRouter()


@router.get(
    "/health",
    response_model=Msg,
    status_code=200,
    include_in_schema=True,
)
def health_check() -> Any:
    return {"msg": "OK"}
