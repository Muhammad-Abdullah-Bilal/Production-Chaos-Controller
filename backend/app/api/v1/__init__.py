from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.schedule import router as schedule_router
from app.api.v1.disruptions import router as disruptions_router
from app.api.v1.production import router as production_router
from app.api.v1.clickhouse import router as clickhouse_router

v1_router = APIRouter()
v1_router.include_router(health_router, tags=["Health"])
v1_router.include_router(schedule_router, prefix="/schedule", tags=["Schedule"])
v1_router.include_router(disruptions_router, prefix="/disruptions", tags=["Disruptions"])
v1_router.include_router(production_router, tags=["Production Layer"])
v1_router.include_router(clickhouse_router, tags=["ClickHouse Analytics & MCP"])

__all__ = ["v1_router"]
