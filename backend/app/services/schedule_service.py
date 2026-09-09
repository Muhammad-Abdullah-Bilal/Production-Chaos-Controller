import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from app.database.session import db_session
from app.models.schedule import ProductionSchedule
from app.models.disruption import DisruptionEvent, DisruptionCreateRequest
from app.models.recovery import RecoveryPlan, PlanStatus, PlanApprovalRequest
from app.scheduling.engine import get_scheduling_engine


class ProductionService:
    """
    Core production service coordinating schedule retrieval,
    disruption tracking, conflict analysis, and recovery approval.
    """

    def __init__(self):
        self.engine = get_scheduling_engine()

    def get_schedule(self, schedule_id: Optional[str] = None) -> Optional[ProductionSchedule]:
        if schedule_id:
            return db_session.schedules.get(schedule_id)
        if db_session.schedules:
            return list(db_session.schedules.values())[0]
        return None

    def list_disruptions(self) -> List[DisruptionEvent]:
        return list(db_session.disruptions.values())

    def get_disruption(self, disruption_id: str) -> Optional[DisruptionEvent]:
        return db_session.disruptions.get(disruption_id)

    def create_disruption(self, request: DisruptionCreateRequest) -> DisruptionEvent:
        schedule = self.get_schedule()
        affected_scenes: List[str] = []
        if schedule:
            affected_scenes = self.engine.detect_conflicts(
                schedule=schedule,
                unavailable_resource_ids=request.affected_resource_ids,
                day_number=request.shoot_day_affected,
            )

        disruption = DisruptionEvent(
            id=f"dis_{uuid.uuid4().hex[:8]}",
            title=request.title,
            description=request.description,
            disruption_type=request.disruption_type,
            severity=request.severity,
            reported_by=request.reported_by or "1st AD",
            reported_at=datetime.now(timezone.utc),
            shoot_day_affected=request.shoot_day_affected,
            affected_resource_ids=request.affected_resource_ids,
            affected_scene_ids=affected_scenes,
            is_active=True,
        )

        db_session.disruptions[disruption.id] = disruption
        return disruption

    def list_recovery_plans(self, disruption_id: Optional[str] = None) -> List[RecoveryPlan]:
        plans = list(db_session.recovery_plans.values())
        if disruption_id:
            return [p for p in plans if p.disruption_id == disruption_id]
        return plans

    def get_recovery_plan(self, plan_id: str) -> Optional[RecoveryPlan]:
        return db_session.recovery_plans.get(plan_id)

    def approve_recovery_plan(self, plan_id: str, request: PlanApprovalRequest) -> Optional[RecoveryPlan]:
        plan = db_session.recovery_plans.get(plan_id)
        if not plan:
            return None

        plan.status = PlanStatus.APPROVED if request.approved else PlanStatus.REJECTED
        plan.human_approved_by = request.approved_by
        plan.human_approved_at = datetime.now(timezone.utc)
        plan.approval_notes = request.notes
        return plan


def get_production_service() -> ProductionService:
    return ProductionService()
