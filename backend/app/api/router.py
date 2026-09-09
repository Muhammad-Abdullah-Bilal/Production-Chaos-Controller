from fastapi import APIRouter
from app.api.v1 import v1_router
from app.api.v1.production import router as production_router
from app.api.v1.disruptions import router as disruptions_router

api_router = APIRouter()
# Direct /api/* routes
api_router.include_router(production_router)
api_router.include_router(disruptions_router, prefix="/disruptions", tags=["Disruptions Direct"])
# Versioned /api/v1/* routes
api_router.include_router(v1_router, prefix="/v1")
