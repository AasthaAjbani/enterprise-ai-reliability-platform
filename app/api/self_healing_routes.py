from fastapi import APIRouter

from app.services.self_healing_service import (
    get_self_healing_status,
)


router = APIRouter(
    prefix="/api",
    tags=["Self Healing"],
)


@router.get(
    "/self-healing"
)
def self_healing_status():

    return get_self_healing_status()