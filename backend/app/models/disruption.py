from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class DisruptionType(str, Enum):
    ACTOR_UNAVAILABLE = "actor_unavailable"
    EQUIPMENT_FAILURE = "equipment_failure"
    LOCATION_UNAVAILABLE = "location_unavailable"
    BAD_WEATHER = "bad_weather"
    CREW_UNAVAILABLE = "crew_unavailable"
    TRANSPORTATION_LOGISTICS = "transportation_logistics"


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DisruptionEvent(BaseModel):
    id: str = Field(..., description="Unique disruption identifier")
    title: str = Field(..., description="Brief headline e.g. Lead Actor hospitalized")
    description: str = Field(..., description="Detailed description of the disruption")
    disruption_type: DisruptionType
    severity: SeverityLevel
    reported_by: str = Field(default="1st AD / Line Producer")
    reported_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    shoot_day_affected: int = Field(..., description="Shoot day number impacted")
    affected_resource_ids: List[str] = Field(default_factory=list)
    affected_scene_ids: List[str] = Field(default_factory=list)
    is_active: bool = True


class DisruptionCreateRequest(BaseModel):
    title: str
    description: str
    disruption_type: DisruptionType
    severity: SeverityLevel
    shoot_day_affected: int
    affected_resource_ids: List[str] = Field(default_factory=list)
    reported_by: Optional[str] = "Line Producer"
