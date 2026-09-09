from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PlanStatus(str, Enum):
    DRAFT = "draft"
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPLIED = "applied"


class ScheduleChange(BaseModel):
    scene_id: str
    scene_number: str
    action: str = Field(..., description="e.g. RESCHEDULED, SWAPPED, POSTPONED, CANCELLED")
    original_day: int
    target_day: int
    reason: str
    resource_substitutions: Dict[str, str] = Field(default_factory=dict)


class ImpactAssessment(BaseModel):
    schedule_variance_days: int = Field(default=0, description="Net shift in total shoot duration")
    cost_variance_usd: float = Field(default=0.0, description="Estimated monetary impact in USD")
    affected_actor_count: int = 0
    affected_crew_count: int = 0
    rescheduled_scene_count: int = 0
    risk_score: float = Field(default=0.0, ge=0.0, le=10.0, description="Risk rating from 0.0 to 10.0")
    key_risks: List[str] = Field(default_factory=list)


class RecoveryPlan(BaseModel):
    id: str
    disruption_id: str
    title: str
    summary: str
    rationale: str = Field(..., description="Why this plan was selected or proposed")
    is_recommended: bool = False
    status: PlanStatus = PlanStatus.PROPOSED
    changes: List[ScheduleChange] = Field(default_factory=list)
    impact: ImpactAssessment
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    human_approved_by: Optional[str] = None
    human_approved_at: Optional[datetime] = None
    approval_notes: Optional[str] = None


class PlanApprovalRequest(BaseModel):
    approved_by: str = Field(..., description="Name/Role of approving Producer")
    notes: Optional[str] = None
    approved: bool = True
