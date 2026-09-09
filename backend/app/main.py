import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import get_settings
from app.api.router import api_router
from app.api.v1.health import router as health_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("production_chaos_controller")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("Starting %s in %s mode", settings.project_name, settings.environment)
    logger.info("CORS origins allowed: %s", settings.cors_origins)
    yield
    logger.info("Shutting down %s", settings.project_name)


settings = get_settings()

app = FastAPI(
    title=settings.project_name,
    version="0.1.0",
    description="Backend API for AI-powered film production disruption recovery & schedule management.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for Next.js frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include root health check for container/load balancer probes
app.include_router(health_router, tags=["Health"])

# Include versioned API router (/api/v1/...)
app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    """Root info endpoint."""
    return {
        "service": settings.project_name,
        "status": "operational",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
        "api_v1": f"{settings.api_v1_prefix}",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.debug)
