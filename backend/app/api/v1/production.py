from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.services.schedule_service import get_production_service
from app.models.schedule import (
    Actor,
    CrewMember,
    Equipment,
    IndoorOutdoor,
    Location,
    PriorityLevel,
    ProductionSchedule,
    Scene,
    ShootingDay,
)

router = APIRouter()


@router.get("/production", response_model=ProductionSchedule)
def get_production_overview():
    """Get overview of 'The Last Signal' production dataset."""
    service = get_production_service()
    schedule = service.get_schedule()
    if not schedule:
        raise HTTPException(status_code=404, detail="Production schedule not found")
    return schedule


@router.get("/scenes", response_model=List[Scene])
def get_scenes(
    location_id: Optional[str] = Query(None, description="Filter scenes by location ID"),
    indoor_outdoor: Optional[IndoorOutdoor] = Query(None, description="Filter by Indoor or Outdoor"),
    priority: Optional[PriorityLevel] = Query(None, description="Filter by priority level"),
):
    """List all 20 scenes with optional filter parameters."""
    service = get_production_service()
    schedule = service.get_schedule()
    if not schedule:
        raise HTTPException(status_code=404, detail="Production schedule not found")

    scenes = schedule.scenes
    if location_id:
        scenes = [s for s in scenes if s.location_id == location_id]
    if indoor_outdoor:
        scenes = [s for s in scenes if s.indoor_outdoor == indoor_outdoor]
    if priority:
        scenes = [s for s in scenes if s.priority == priority]

    return scenes


@router.get("/actors", response_model=List[Actor])
def get_actors():
    """List all 8 cast members for 'The Last Signal'."""
    service = get_production_service()
    schedule = service.get_schedule()
    if not schedule:
        raise HTTPException(status_code=404, detail="Production schedule not found")
    return schedule.actors


@router.get("/crew", response_model=List[CrewMember])
def get_crew():
    """List all 10 crew members."""
    service = get_production_service()
    schedule = service.get_schedule()
    if not schedule:
        raise HTTPException(status_code=404, detail="Production schedule not found")
    return schedule.crew


@router.get("/locations", response_model=List[Location])
def get_locations():
    """List all 4 filming locations."""
    service = get_production_service()
    schedule = service.get_schedule()
    if not schedule:
        raise HTTPException(status_code=404, detail="Production schedule not found")
    return schedule.locations


@router.get("/equipment", response_model=List[Equipment])
def get_equipment():
    """List all 5 equipment packages."""
    service = get_production_service()
    schedule = service.get_schedule()
    if not schedule:
        raise HTTPException(status_code=404, detail="Production schedule not found")
    return schedule.equipment


@router.get("/schedule", response_model=List[ShootingDay])
def get_shooting_days():
    """List all 10 shooting days with mapped scenes."""
    service = get_production_service()
    schedule = service.get_schedule()
    if not schedule:
        raise HTTPException(status_code=404, detail="Production schedule not found")
    return schedule.shooting_days
