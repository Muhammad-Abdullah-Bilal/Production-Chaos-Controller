from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.services.schedule_service import get_production_service
from app.models.schedule import ProductionSchedule, Scene, Actor, CrewMember, Location, Equipment
from app.scheduling.engine import get_scheduling_engine

router = APIRouter()


@router.get("", response_model=ProductionSchedule)
def get_current_schedule(schedule_id: Optional[str] = Query(None, description="Optional schedule ID")):
    """Get production schedule by ID or active default schedule."""
    service = get_production_service()
    schedule = service.get_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Production schedule not found")
    return schedule


@router.get("/scenes", response_model=List[Scene])
def get_scenes(schedule_id: Optional[str] = None):
    """List all scheduled scenes for the production."""
    service = get_production_service()
    schedule = service.get_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Production schedule not found")
    return schedule.scenes


@router.get("/validate")
def validate_schedule(schedule_id: Optional[str] = None):
    """Run deterministic integrity validation on the production schedule."""
    service = get_production_service()
    schedule = service.get_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Production schedule not found")
    engine = get_scheduling_engine()
    return engine.validate_schedule_integrity(schedule)
