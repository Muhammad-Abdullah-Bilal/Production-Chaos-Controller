from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field
from app.services.schedule_service import get_production_service
from app.models.disruption import DisruptionEvent, DisruptionCreateRequest
from app.models.recovery import RecoveryPlan, PlanApprovalRequest
from app.agent.orchestrator import get_agent_orchestrator, get_production_manager_agent

router = APIRouter()


class ActorDisruptionRequest(BaseModel):
    actor_id: str = Field(..., description="Unique actor ID e.g. act_01 (Dr. Sarah Mercer)")
    shoot_day: int = Field(..., description="Shooting day number e.g. 4")
    reason: str = Field(
        default="Actor suddenly contractually unavailable on specified shoot day.",
        description="Reason for disruption",
    )


class EquipmentDisruptionRequest(BaseModel):
    equipment_id: str = Field(..., description="Unique equipment ID e.g. eq_01 (RED V-Raptor 8K Package)")
    shoot_day: int = Field(..., description="Shooting day number e.g. 5")
    reason: str = Field(
        default="Camera A / Equipment package experienced critical technical failure on shoot day.",
        description="Failure description",
    )


class LocationDisruptionRequest(BaseModel):
    location_id: str = Field(..., description="Unique location ID e.g. loc_03 (Sub-Zero Quantum Vault)")
    shoot_day: int = Field(..., description="Shooting day number e.g. 6")
    reason: str = Field(
        default="Location suddenly unavailable due to emergency maintenance/lockdown on shoot day.",
        description="Unavailability description",
    )


class WeatherDisruptionRequest(BaseModel):
    weather_type: str = Field(default="Heavy Rain", description="Weather condition e.g. Heavy Rain, Snow, Blizzard, High Winds")
    severity: str = Field(default="High", description="Severity level: High, Medium, Low")
    shoot_day: int = Field(default=7, description="Shooting day number e.g. 7")
    reason: str = Field(
        default="Severe torrential rain forecast halting outdoor filming at Glacier Pass.",
        description="Forecast description",
    )


class CrewDisruptionRequest(BaseModel):
    crew_id: str = Field(..., description="Unique crew ID e.g. crw_02 (Claire Delacroix - Director of Photography)")
    shoot_day: int = Field(..., description="Shooting day number e.g. 5")
    reason: str = Field(
        default="Director of Photography suddenly unavailable on shoot day.",
        description="Reason for crew unavailability",
    )


class LogisticsDisruptionRequest(BaseModel):
    vehicle_id: str = Field(default="veh_01", description="Unique vehicle ID e.g. veh_01 (Camera & Grip Transport Van #1)")
    shoot_day: int = Field(default=8, description="Shooting day number e.g. 8")
    delay_hours: int = Field(default=2, description="Estimated arrival delay in hours")
    reason: str = Field(
        default="Equipment transport vehicle broken down on mountain pass highway route.",
        description="Reason for transport breakdown",
    )


class DisruptionAnalyzeRequest(BaseModel):
    disruption_type: str = Field(..., description="Disruption type: actor_unavailable, equipment_failure, location_unavailable, bad_weather, crew_unavailable, logistics_failure")
    resource_id: str = Field(..., description="Resource ID e.g. act_01, eq_01, loc_03, crw_02, veh_01")
    shoot_day: int = Field(..., description="Shooting day number e.g. 4")
    reason: Optional[str] = Field(default="", description="Reason for disruption")
    extra_params: Optional[Dict[str, Any]] = Field(default=None, description="Optional extra parameters")


class MultiDisruptionItem(BaseModel):
    disruption_type: str = Field(..., description="Type: actor_unavailable, equipment_failure, location_unavailable, bad_weather, crew_unavailable, logistics_failure")
    resource_id: str = Field(..., description="Resource ID e.g. act_01, eq_01, loc_03, crw_02, veh_01")
    shoot_day: int = Field(default=6, description="Shooting day number e.g. 6")
    reason: Optional[str] = Field(default="", description="Description of disruption")
    weather_type: Optional[str] = Field(default="Heavy Rain", description="Weather condition if applicable")
    severity: Optional[str] = Field(default="High", description="Severity level if applicable")


class MultiDisruptionAnalyzeRequest(BaseModel):
    disruptions: List[MultiDisruptionItem] = Field(..., description="List of simultaneous disruptions occurring on a shoot day")


@router.post("/analyze")
def analyze_disruption_with_agent(request: DisruptionAnalyzeRequest) -> Dict[str, Any]:
    """
    Central Production Manager Agent endpoint.
    Executes the 10-step agent workflow using deterministic tool calling, multi-step trace logging,
    and Google Gemini orchestration across all 6 supported disruption scenarios.
    """
    if not request.resource_id or not request.resource_id.strip():
        raise HTTPException(status_code=400, detail="Resource ID cannot be empty.")
    if request.shoot_day < 1 or request.shoot_day > 20:
        raise HTTPException(status_code=400, detail=f"Invalid shoot day {request.shoot_day}. Must be between 1 and 20.")

    agent = get_production_manager_agent()
    return agent.analyze_disruption(
        disruption_type=request.disruption_type,
        resource_id=request.resource_id,
        shoot_day=request.shoot_day,
        reason=request.reason or "",
        extra_params=request.extra_params,
    )


@router.post("/multi-analyze")
def analyze_multi_disruptions(request: MultiDisruptionAnalyzeRequest) -> Dict[str, Any]:
    """
    Central Production Manager Agent Chaos Mode endpoint.
    Analyzes multiple simultaneous disruptions together, builds combined dependency graph,
    detects recovery conflicts between single-disruption plans, and generates unified recovery strategies.
    """
    if not request.disruptions:
        raise HTTPException(status_code=400, detail="Multi-disruption list cannot be empty.")

    for dis in request.disruptions:
        if dis.shoot_day < 1 or dis.shoot_day > 20:
            raise HTTPException(status_code=400, detail=f"Invalid shoot day {dis.shoot_day} in multi-disruption stack.")

    agent = get_production_manager_agent()
    disruption_list = [item.model_dump(mode="json") for item in request.disruptions]
    return agent.process_multi_disruption(disruptions=disruption_list)




@router.post("/actor-unavailable")
def handle_actor_disruption(request: ActorDisruptionRequest) -> Dict[str, Any]:
    """
    Process actor unavailability disruption scenario.
    Invokes deterministic scheduling tools, evaluates dependencies, generates candidate recovery options,
    and returns a structured AI agent analysis response.
    """
    orchestrator = get_agent_orchestrator()
    analysis = orchestrator.process_actor_disruption(
        actor_id=request.actor_id,
        shoot_day=request.shoot_day,
        reason=request.reason,
    )
    return analysis


@router.post("/equipment-failure")
def handle_equipment_disruption(request: EquipmentDisruptionRequest) -> Dict[str, Any]:
    """
    Process equipment failure disruption scenario.
    Invokes deterministic equipment tools, evaluates compatibility & crew qualifications,
    generates ranked candidate recovery plans, and returns a structured AI agent response.
    """
    orchestrator = get_agent_orchestrator()
    analysis = orchestrator.process_equipment_disruption(
        equipment_id=request.equipment_id,
        shoot_day=request.shoot_day,
        reason=request.reason,
    )
    return analysis


@router.post("/location-unavailable")
def handle_location_disruption(request: LocationDisruptionRequest) -> Dict[str, Any]:
    """
    Process location unavailability disruption scenario.
    Invokes deterministic location tools, evaluates alternative approved locations & requirements,
    generates ranked candidate recovery plans, and returns a structured AI agent response.
    """
    orchestrator = get_agent_orchestrator()
    analysis = orchestrator.process_location_disruption(
        location_id=request.location_id,
        shoot_day=request.shoot_day,
        reason=request.reason,
    )
    return analysis


@router.post("/bad-weather")
def handle_weather_disruption(request: WeatherDisruptionRequest) -> Dict[str, Any]:
    """
    Process bad weather disruption scenario.
    Invokes deterministic weather tools, identifies stalled outdoor scenes & indoor cover sets,
    generates ranked candidate recovery plans, and returns a structured AI agent response.
    """
    orchestrator = get_agent_orchestrator()
    analysis = orchestrator.process_weather_disruption(
        weather_type=request.weather_type,
        severity=request.severity,
        shoot_day=request.shoot_day,
        description=request.reason,
    )
    return analysis


@router.post("/crew-unavailable")
def handle_crew_disruption(request: CrewDisruptionRequest) -> Dict[str, Any]:
    """
    Process crew unavailability disruption scenario.
    Invokes deterministic crew tools, evaluates replacement qualifications & schedules,
    generates ranked candidate recovery plans, and returns a structured AI agent response.
    """
    orchestrator = get_agent_orchestrator()
    analysis = orchestrator.process_crew_disruption(
        crew_id=request.crew_id,
        shoot_day=request.shoot_day,
        reason=request.reason,
    )
    return analysis


@router.post("/logistics-delay")
def handle_logistics_disruption(request: LogisticsDisruptionRequest) -> Dict[str, Any]:
    """
    Process transportation / logistics breakdown disruption scenario.
    Invokes deterministic logistics tools, checks vehicle dispatch feasibility & delay impact,
    generates ranked candidate recovery plans, and returns a structured AI agent response.
    """
    orchestrator = get_agent_orchestrator()
    analysis = orchestrator.process_logistics_disruption(
        vehicle_id=request.vehicle_id,
        shoot_day=request.shoot_day,
        reason=request.reason,
        delay_hours=request.delay_hours,
    )
    return analysis






@router.get("", response_model=List[DisruptionEvent])
def list_disruptions():
    """List all active and historical production disruptions."""
    service = get_production_service()
    return service.list_disruptions()


@router.post("", response_model=DisruptionEvent, status_code=201)
def create_disruption(request: DisruptionCreateRequest):
    """
    Log a new production disruption event.
    Automatically runs deterministic conflict detection against the schedule.
    """
    service = get_production_service()
    return service.create_disruption(request)


@router.get("/{disruption_id}", response_model=DisruptionEvent)
def get_disruption(disruption_id: str = Path(..., description="The disruption event ID")):
    """Get details of a specific disruption event."""
    service = get_production_service()
    disruption = service.get_disruption(disruption_id)
    if not disruption:
        raise HTTPException(status_code=404, detail="Disruption not found")
    return disruption


@router.get("/{disruption_id}/plans", response_model=List[RecoveryPlan])
def list_recovery_plans_for_disruption(disruption_id: str):
    """List recovery plans associated with a disruption."""
    service = get_production_service()
    return service.list_recovery_plans(disruption_id)


@router.post("/plans/{plan_id}/approve", response_model=RecoveryPlan)
def approve_recovery_plan(plan_id: str, request: PlanApprovalRequest):
    """
    Human-in-the-loop approval or rejection of an AI-generated recovery plan.
    Enforces producer sign-off before schedule modifications can be applied.
    """
    service = get_production_service()
    plan = service.approve_recovery_plan(plan_id, request)
    if not plan:
        raise HTTPException(status_code=404, detail="Recovery plan not found")
    return plan
