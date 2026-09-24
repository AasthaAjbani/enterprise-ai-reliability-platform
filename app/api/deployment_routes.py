from fastapi import APIRouter

from app.services.deployment_service import (
    get_deployment_status,
)


router = APIRouter(
    prefix="/api",
    tags=["Model Deployment"],
)


# =========================================================
# DEPLOYMENT STATUS
# =========================================================

@router.get(
    "/deployment"
)
def deployment_status():

    return get_deployment_status()