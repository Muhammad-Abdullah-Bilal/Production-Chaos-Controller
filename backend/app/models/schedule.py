from datetime import date
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class IndoorOutdoor(str, Enum):
    INDOOR = "Indoor"
    OUTDOOR = "Outdoor"


class PriorityLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class SceneStatus(str, Enum):
    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    MOVEABLE = "Moveable"
    HARD_FIXED = "Hard Fixed"


class Actor(BaseModel):
    actor_id: str = Field(..., description="Unique actor ID e.g. act_01")
    name: str
    character_name: str
    is_lead: bool = False
    daily_rate: float = Field(default=0.0, description="Daily rate in USD")
    contact_info: Optional[str] = None
    availability_notes: Optional[str] = None


class CrewMember(BaseModel):
    crew_id: str = Field(..., description="Unique crew member ID e.g. crw_01")
    name: str
    department: str = Field(..., description="e.g. Camera, Sound, Lighting, Directing, Stunts")
    role: str = Field(..., description="e.g. Director of Photography, Gaffer, 1st AD")
    daily_rate: float = Field(default=0.0, description="Daily rate in USD")


class Location(BaseModel):
    location_id: str = Field(..., description="Unique location ID e.g. loc_01")
    name: str
    address: str
    indoor_outdoor: IndoorOutdoor
    daily_rate: float = Field(default=0.0, description="Cost per day in USD")
    permit_required: bool = False
    weather_vulnerable: bool = False
    notes: Optional[str] = None


class Equipment(BaseModel):
    equipment_id: str = Field(..., description="Unique equipment ID e.g. eq_01")
    name: str
    category: str = Field(..., description="e.g. Camera, Lighting, Sound, Crane, SFX")
    daily_rate: float = Field(default=0.0, description="Daily rental rate in USD")
    is_critical: bool = False


class Scene(BaseModel):
    scene_id: str = Field(..., description="Unique scene ID e.g. sc_01")
    scene_number: str = Field(..., description="Scene number e.g. 1A")
    title: str
    description: str
    shooting_date: str = Field(..., description="Target date string YYYY-MM-DD")
    start_time: str = Field(default="08:00", description="HH:MM format")
    duration: float = Field(default=2.0, description="Duration in hours")
    location_id: str
    actor_ids: List[str] = Field(default_factory=list)
    crew_ids: List[str] = Field(default_factory=list)
    equipment_ids: List[str] = Field(default_factory=list)
    estimated_cost: float = Field(default=0.0, description="Estimated scene budget in USD")
    priority: PriorityLevel = PriorityLevel.MEDIUM
    indoor_outdoor: IndoorOutdoor = IndoorOutdoor.INDOOR
    weather_sensitive: bool = False
    required_weather: Optional[str] = Field(default="Clear / Dry", description="Required weather condition e.g. Clear / Dry, Overcast, Any")
    status: SceneStatus = SceneStatus.SCHEDULED


class ShootingDay(BaseModel):
    day_number: int = Field(..., description="Shooting day index 1..10")
    date: str = Field(..., description="YYYY-MM-DD")
    call_time: str = "06:00"
    wrap_time: str = "18:00"
    location_id: str
    scene_ids: List[str] = Field(default_factory=list)
    estimated_daily_cost: float = 0.0
    notes: Optional[str] = None


class ProductionSchedule(BaseModel):
    id: str
    project_title: str = "The Last Signal"
    director: str = "Elena Rostova"
    producer: str = "Marcus Webb"
    total_budget: float = 5500000.0
    daily_burn_rate: float = 85000.0
    start_date: str = "2026-10-01"
    total_days: int = 10
    scenes: List[Scene] = Field(default_factory=list)
    actors: List[Actor] = Field(default_factory=list)
    crew: List[CrewMember] = Field(default_factory=list)
    locations: List[Location] = Field(default_factory=list)
    equipment: List[Equipment] = Field(default_factory=list)
    shooting_days: List[ShootingDay] = Field(default_factory=list)
