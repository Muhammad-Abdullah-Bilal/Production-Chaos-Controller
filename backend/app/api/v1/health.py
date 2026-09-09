from datetime import datetime, timezone
from fastapi import APIRouter
from app.config.settings import get_settings
from app.database.clickhouse import get_clickhouse_client
from app.agent.orchestrator import get_agent_orchestrator
from app.database.session import db_session

router = APIRouter()


@router.get("/health")
def health_check():
    """
    Comprehensive service health check endpoint.
    Returns backend readiness, runtime environment, and integration status.
    """
    settings = get_settings()
    clickhouse = get_clickhouse_client()
    orchestrator = get_agent_orchestrator()

    return {
        "status": "healthy",
        "service": settings.project_name,
        "version": "0.1.0",
        "environment": settings.environment,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "integrations": {
            "clickhouse": clickhouse.check_connection(),
            "agent_orchestrator": {
                "ready": True,
                "configured": orchestrator.is_configured(),
                "registered_tools_count": len(orchestrator.tools),
            },
            "database": {
                "active_schedules": len(db_session.schedules),
                "recorded_disruptions": len(db_session.disruptions),
            },
        },
    }
