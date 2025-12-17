from fastapi import APIRouter

from app.api.v1.endpoints import interactions, patients, outcomes

api_router = APIRouter()
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(
    interactions.router, prefix="/interactions", tags=["interactions"]
)
api_router.include_router(outcomes.router, prefix="/outcomes", tags=["configuration"])
