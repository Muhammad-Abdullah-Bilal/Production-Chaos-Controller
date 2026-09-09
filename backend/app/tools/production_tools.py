"""
Deterministic application tools callable by Google Gemini / Google Cloud Agent Builder.
All calculations, lookups, and constraint validations are strictly executed by deterministic Python functions.
"""

from typing import Any, Dict, List, Optional
from app.database.session import db_session
from app.scheduling.engine import get_scheduling_engine


# --- ACTOR DISRUPTION TOOLS ---

def find_affected_scenes_tool(actor_id: str, shoot_day: int) -> List[Dict[str, Any]]:
    """
    Deterministic Tool: Find every scene scheduled for shoot_day requiring actor_id.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    scenes = engine.find_affected_scenes(schedule, actor_id, shoot_day)
    return [s.model_dump(mode="json") for s in scenes]


def find_available_scenes_tool(day_number: int, unavailable_actor_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Deterministic Tool: Find unshot scenes from future days that do NOT require unavailable actors.
    """
    schedule = list(db_session.schedules.values())[0]
    unavail_set = set(unavailable_actor_ids)
    available: List[Dict[str, Any]] = []

    for scene in schedule.scenes:
        if set(scene.actor_ids).intersection(unavail_set):
            continue
        available.append(scene.model_dump(mode="json"))

    return available


def check_location_availability_tool(location_id: str, day_number: int) -> Dict[str, Any]:
    """
    Deterministic Tool: Check if a filming location is available for day_number.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    is_available = engine.check_location_availability(schedule, location_id, day_number)
    return {"location_id": location_id, "day_number": day_number, "is_available": is_available}


def check_equipment_availability_tool(equipment_ids: List[str], day_number: int) -> Dict[str, Any]:
    """
    Deterministic Tool: Verify equipment availability for day_number.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    is_available = engine.check_equipment_availability(schedule, equipment_ids, day_number)
    return {"equipment_ids": equipment_ids, "day_number": day_number, "is_available": is_available}


def check_crew_availability_tool(crew_ids: List[str], day_number: int) -> Dict[str, Any]:
    """
    Deterministic Tool: Verify crew availability for day_number.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    is_available = engine.check_crew_availability(schedule, crew_ids, day_number)
    return {"crew_ids": crew_ids, "day_number": day_number, "is_available": is_available}


def calculate_schedule_impact_tool(original_days: int, new_days: int) -> Dict[str, Any]:
    """
    Deterministic Tool: Calculate net schedule delay variance.
    """
    engine = get_scheduling_engine()
    return engine.calculate_schedule_impact(original_days, new_days)


def calculate_cost_impact_tool(rescheduled_scene_ids: List[str], shift_days: int) -> Dict[str, Any]:
    """
    Deterministic Tool: Calculate monetary cost impact based on daily burn rate.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    scene_map = {s.scene_id: s for s in schedule.scenes}
    rescheduled_scenes = [scene_map[sid] for sid in rescheduled_scene_ids if sid in scene_map]
    return engine.calculate_cost_impact(rescheduled_scenes, shift_days, schedule.daily_burn_rate)


def generate_recovery_options_tool(actor_id: str, shoot_day: int) -> List[Dict[str, Any]]:
    """
    Deterministic Tool: Generate and rank candidate recovery options for actor disruption.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    return engine.generate_recovery_options(schedule, actor_id, shoot_day)


# --- EQUIPMENT FAILURE DETERMINISTIC TOOLS ---

def find_equipment_dependencies_tool(equipment_id: str, shoot_day: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Deterministic Tool: Identify all scenes requiring the failed equipment.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    scenes = engine.find_equipment_dependencies(schedule, equipment_id, shoot_day)
    return [s.model_dump(mode="json") for s in scenes]


def find_alternative_equipment_tool(equipment_id: str) -> List[Dict[str, Any]]:
    """
    Deterministic Tool: Determine whether alternative equipment is available in the same category.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    alts = engine.find_alternative_equipment(schedule, equipment_id)
    return [a.model_dump(mode="json") for a in alts]


def check_equipment_compatibility_tool(equipment_id: str, scene_id: str) -> Dict[str, Any]:
    """
    Deterministic Tool: Check whether alternative equipment is compatible with scene technical specs.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    is_compat = engine.check_equipment_compatibility(schedule, equipment_id, scene_id)
    return {"equipment_id": equipment_id, "scene_id": scene_id, "is_compatible": is_compat}


def check_crew_for_equipment_tool(equipment_id: str, crew_ids: List[str]) -> Dict[str, Any]:
    """
    Deterministic Tool: Check whether required crew members are qualified to operate the alternative equipment.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    is_qualified = engine.check_crew_for_equipment(schedule, equipment_id, crew_ids)
    return {"equipment_id": equipment_id, "crew_ids": crew_ids, "is_qualified": is_qualified}


def calculate_equipment_impact_tool(equipment_id: str, shoot_day: int) -> Dict[str, Any]:
    """
    Deterministic Tool: Calculate cost and schedule impact for equipment failure.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    return engine.calculate_equipment_impact(schedule, equipment_id, shoot_day)


def generate_equipment_recovery_options_tool(equipment_id: str, shoot_day: int) -> List[Dict[str, Any]]:
    """
    Deterministic Tool: Generate and rank candidate recovery options for equipment failure.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    return engine.generate_equipment_recovery_options(schedule, equipment_id, shoot_day)


# --- LOCATION UNAVAILABLE DETERMINISTIC TOOLS ---

def find_location_dependencies_tool(location_id: str, shoot_day: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Deterministic Tool: Identify all scenes depending on location_id (overall or on shoot_day).
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    scenes = engine.find_location_dependencies(schedule, location_id, shoot_day)
    return [s.model_dump(mode="json") for s in scenes]


def find_alternative_locations_tool(location_id: str) -> List[Dict[str, Any]]:
    """
    Deterministic Tool: Find approved alternative locations matching scene specs and criteria.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    locs = engine.find_alternative_locations(schedule, location_id)
    return [l.model_dump(mode="json") for l in locs]


def check_location_requirements_tool(location_id: str, scene_id: str) -> Dict[str, Any]:
    """
    Deterministic Tool: Check whether an alternative location supports scene specifications.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    return engine.check_location_requirements(schedule, location_id, scene_id)


def check_resource_availability_tool(scene_ids: List[str], shoot_day: int) -> Dict[str, Any]:
    """
    Deterministic Tool: Verify whether required actors, crew, and equipment are available for scene_ids on shoot_day.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    return engine.check_resource_availability(schedule, scene_ids, shoot_day)


def calculate_location_impact_tool(location_id: str, shoot_day: int) -> Dict[str, Any]:
    """
    Deterministic Tool: Calculate cost, delay, resource count, and moved scenes impact for location failure.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    return engine.calculate_location_impact(schedule, location_id, shoot_day)


def generate_location_recovery_options_tool(location_id: str, shoot_day: int) -> List[Dict[str, Any]]:
    """
    Deterministic Tool: Generate and rank candidate recovery options for location failure.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    return engine.generate_location_recovery_options(schedule, location_id, shoot_day)


# --- BAD WEATHER DISRUPTION DETERMINISTIC TOOLS ---

def find_weather_affected_scenes_tool(shoot_day: int, weather_type: str, severity: str) -> List[Dict[str, Any]]:
    """
    Deterministic Tool: Identify all outdoor and weather-sensitive scenes affected by severe weather on shoot_day.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    scenes = engine.find_weather_affected_scenes(schedule, shoot_day, weather_type, severity)
    return [s.model_dump(mode="json") for s in scenes]


def find_indoor_cover_scenes_tool(shoot_day: int) -> List[Dict[str, Any]]:
    """
    Deterministic Tool: Find available indoor cover set scenes from future days that can be moved into shoot_day.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    covers = engine.find_indoor_cover_scenes(schedule, shoot_day)
    return [c.model_dump(mode="json") for c in covers]


def find_alternative_outdoor_dates_tool(affected_scene_ids: List[str], shoot_day: int) -> List[Dict[str, Any]]:
    """
    Deterministic Tool: Find future clear-weather dates suitable for rescheduling outdoor scenes.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    return engine.find_alternative_outdoor_dates(schedule, affected_scene_ids, shoot_day)


def generate_weather_recovery_options_tool(weather_type: str, severity: str, shoot_day: int) -> List[Dict[str, Any]]:
    """
    Deterministic Tool: Generate and rank candidate recovery options for bad weather disruption.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    return engine.generate_weather_recovery_options(schedule, weather_type, severity, shoot_day)


# --- CREW UNAVAILABLE DETERMINISTIC TOOLS ---

def find_crew_dependencies_tool(crew_id: str, shoot_day: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Deterministic Tool: Identify all scenes depending on crew_id (overall or on shoot_day).
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    scenes = engine.find_crew_dependencies(schedule, crew_id, shoot_day)
    return [s.model_dump(mode="json") for s in scenes]


def find_qualified_replacement_crew_tool(crew_id: str) -> List[Dict[str, Any]]:
    """
    Deterministic Tool: Find qualified replacement crew members matching department & role.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    return engine.find_qualified_replacement_crew(schedule, crew_id)


def check_crew_schedule_tool(crew_id: str, target_day: int) -> Dict[str, Any]:
    """
    Deterministic Tool: Verify whether a crew member is available on target_day.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    return engine.check_crew_schedule(schedule, crew_id, target_day)


def calculate_crew_impact_tool(crew_id: str, shoot_day: int) -> Dict[str, Any]:
    """
    Deterministic Tool: Calculate cost and schedule impact for crew unavailability.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    return engine.calculate_crew_impact(schedule, crew_id, shoot_day)


def generate_crew_recovery_options_tool(crew_id: str, shoot_day: int) -> List[Dict[str, Any]]:
    """
    Deterministic Tool: Generate and rank candidate recovery options for crew unavailability.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    return engine.generate_crew_recovery_options(schedule, crew_id, shoot_day)


# --- TRANSPORTATION / LOGISTICS DISRUPTION DETERMINISTIC TOOLS ---

def find_logistics_dependencies_tool(vehicle_id: str, shoot_day: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Deterministic Tool: Identify all scenes depending on delayed transport/vehicle on shoot_day.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    scenes = engine.find_logistics_dependencies(schedule, vehicle_id, shoot_day)
    return [s.model_dump(mode="json") for s in scenes]


def check_vehicle_dispatch_feasibility_tool(vehicle_id: str, shoot_day: int) -> Dict[str, Any]:
    """
    Deterministic Tool: Check backup hot-shot transport availability and ETA delay.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    return engine.check_vehicle_dispatch_feasibility(schedule, vehicle_id, shoot_day)


def calculate_logistics_impact_tool(vehicle_id: str, shoot_day: int) -> Dict[str, Any]:
    """
    Deterministic Tool: Calculate cost and delay impact for logistics/transport breakdown.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    return engine.calculate_logistics_impact(schedule, vehicle_id, shoot_day)


def generate_logistics_recovery_options_tool(vehicle_id: str, shoot_day: int, delay_hours: int = 2) -> List[Dict[str, Any]]:
    """
    Deterministic Tool: Generate and rank candidate recovery options for transport breakdown.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    return engine.generate_logistics_recovery_options(schedule, vehicle_id, shoot_day, delay_hours)


# --- CANONICAL PRODUCTION MANAGER AGENT TOOLS ---

def get_production_schedule() -> Dict[str, Any]:
    """
    Deterministic Tool: Retrieve the master production schedule including scenes, cast, crew, locations, equipment, and shooting days.
    """
    schedule = list(db_session.schedules.values())[0]
    return schedule.model_dump(mode="json")


def get_scene(scene_id: str) -> Dict[str, Any]:
    """
    Deterministic Tool: Get details for a specific scene by scene_id.
    """
    schedule = list(db_session.schedules.values())[0]
    scene = next((s for s in schedule.scenes if s.scene_id == scene_id), None)
    if not scene:
        return {"error": f"Scene {scene_id} not found."}
    return scene.model_dump(mode="json")


def find_affected_scenes(resource_id: str, shoot_day: int) -> List[Dict[str, Any]]:
    """
    Deterministic Tool: Find every scene scheduled for shoot_day requiring resource_id (actor, equipment, location, crew, or vehicle).
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    scenes = engine.find_resource_dependencies(schedule, "actor", resource_id, shoot_day)
    if not scenes:
        scenes = engine.find_resource_dependencies(schedule, "crew", resource_id, shoot_day)
    if not scenes:
        scenes = engine.find_resource_dependencies(schedule, "equipment", resource_id, shoot_day)
    if not scenes:
        scenes = engine.find_resource_dependencies(schedule, "location", resource_id, shoot_day)
    if not scenes:
        scenes = engine.find_affected_scenes(schedule, resource_id, shoot_day)
    return [s.model_dump(mode="json") for s in scenes]


def find_resource_dependencies(resource_type: str, resource_id: str, shoot_day: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Deterministic Tool: Universal dependency analysis finding all scenes requiring a given resource.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    scenes = engine.find_resource_dependencies(schedule, resource_type, resource_id, shoot_day)
    return [s.model_dump(mode="json") for s in scenes]


def check_actor_availability(actor_id: str, shoot_day: int) -> Dict[str, Any]:
    """
    Deterministic Tool: Check if an actor is available on shoot_day.
    """
    schedule = list(db_session.schedules.values())[0]
    actor = next((a for a in schedule.actors if a.actor_id == actor_id), None)
    return {
        "actor_id": actor_id,
        "actor_name": actor.name if actor else actor_id,
        "shoot_day": shoot_day,
        "is_available": actor is not None,
    }


def check_crew_availability(crew_ids: List[str], shoot_day: int) -> Dict[str, Any]:
    """
    Deterministic Tool: Verify crew availability for shoot_day.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    is_available = engine.check_crew_availability(schedule, crew_ids, shoot_day)
    return {"crew_ids": crew_ids, "shoot_day": shoot_day, "is_available": is_available}


def check_location_availability(location_id: str, shoot_day: int) -> Dict[str, Any]:
    """
    Deterministic Tool: Check if a filming location is available for shoot_day.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    is_available = engine.check_location_availability(schedule, location_id, shoot_day)
    return {"location_id": location_id, "shoot_day": shoot_day, "is_available": is_available}


def check_equipment_availability(equipment_ids: List[str], shoot_day: int) -> Dict[str, Any]:
    """
    Deterministic Tool: Verify equipment availability for shoot_day.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    is_available = engine.check_equipment_availability(schedule, equipment_ids, shoot_day)
    return {"equipment_ids": equipment_ids, "shoot_day": shoot_day, "is_available": is_available}


def find_alternative_scenes(shoot_day: int, unavailable_resource_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Deterministic Tool: Search for alternative unshot cover set / indoor scenes from future days.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    covers = engine.find_indoor_cover_scenes(schedule, shoot_day)
    if unavailable_resource_ids:
        unavail = set(unavailable_resource_ids)
        covers = [c for c in covers if not (set(c.actor_ids).intersection(unavail) or set(c.crew_ids).intersection(unavail))]
    return [c.model_dump(mode="json") for c in covers]


def find_alternative_resources(resource_type: str, resource_id: str) -> List[Dict[str, Any]]:
    """
    Deterministic Tool: Find alternative backup resources (locations, equipment, or crew) for a disrupted resource.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    if resource_type == "location":
        return [l.model_dump(mode="json") for l in engine.find_alternative_locations(schedule, resource_id)]
    elif resource_type == "equipment":
        return [e.model_dump(mode="json") for e in engine.find_alternative_equipment(schedule, resource_id)]
    elif resource_type == "crew":
        return engine.find_qualified_replacement_crew(schedule, resource_id)
    return []


def calculate_schedule_impact(original_days: int, new_days: int) -> Dict[str, Any]:
    """
    Deterministic Tool: Calculate net schedule delay variance.
    """
    engine = get_scheduling_engine()
    return engine.calculate_schedule_impact(original_days, new_days)


def calculate_cost_impact(rescheduled_scene_ids: List[str], shift_days: int) -> Dict[str, Any]:
    """
    Deterministic Tool: Calculate monetary cost impact based on daily burn rate.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    scene_map = {s.scene_id: s for s in schedule.scenes}
    rescheduled_scenes = [scene_map[sid] for sid in rescheduled_scene_ids if sid in scene_map]
    return engine.calculate_cost_impact(rescheduled_scenes, shift_days, schedule.daily_burn_rate)


def generate_recovery_options(disruption_type: str, resource_id: str, shoot_day: int) -> List[Dict[str, Any]]:
    """
    Deterministic Tool: Generate and rank candidate recovery plans for any disruption type.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]

    if disruption_type in ("actor_unavailable", "actor"):
        return engine.generate_recovery_options(schedule, resource_id, shoot_day)
    elif disruption_type in ("equipment_failure", "equipment"):
        return engine.generate_equipment_recovery_options(schedule, resource_id, shoot_day)
    elif disruption_type in ("location_unavailable", "location"):
        return engine.generate_location_recovery_options(schedule, resource_id, shoot_day)
    elif disruption_type in ("bad_weather", "weather"):
        return engine.generate_weather_recovery_options(schedule, "Heavy Rain", "High", shoot_day)
    elif disruption_type in ("crew_unavailable", "crew"):
        return engine.generate_crew_recovery_options(schedule, resource_id, shoot_day)
    elif disruption_type in ("logistics_failure", "logistics_delay", "logistics"):
        return engine.generate_logistics_recovery_options(schedule, resource_id, shoot_day)
    
    return engine.generate_recovery_options(schedule, resource_id, shoot_day)


def analyze_multi_disruptions_tool(disruptions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Deterministic Tool: Analyze multiple simultaneous disruptions, build combined dependency graph, detect recovery conflicts, and generate unified recovery options.
    """
    engine = get_scheduling_engine()
    schedule = list(db_session.schedules.values())[0]
    graph = engine.build_multi_disruption_dependency_graph(schedule, disruptions)
    conflicts = engine.detect_recovery_conflicts(schedule, disruptions)
    recovery_options = engine.generate_combined_recovery_options(schedule, disruptions)

    return {
        "graph": graph,
        "conflicts": conflicts,
        "recovery_options": recovery_options,
    }


# --- CLICKHOUSE ANALYTICS DETERMINISTIC TOOLS ---

def query_clickhouse_actor_scenes_tool(actor_id: str) -> Dict[str, Any]:
    """
    Deterministic Tool: Query ClickHouse to find all scenes dependent on actor_id.
    """
    from app.database.clickhouse import get_clickhouse_client
    ch = get_clickhouse_client()
    schedule = list(db_session.schedules.values())[0]
    return ch.query_scenes_by_actor(actor_id, schedule)


def query_clickhouse_equipment_scenes_tool(equipment_id: str) -> Dict[str, Any]:
    """
    Deterministic Tool: Query ClickHouse to find all scenes utilizing equipment_id.
    """
    from app.database.clickhouse import get_clickhouse_client
    ch = get_clickhouse_client()
    schedule = list(db_session.schedules.values())[0]
    return ch.query_scenes_by_equipment(equipment_id, schedule)


def query_clickhouse_location_frequency_tool(limit: int = 5) -> Dict[str, Any]:
    """
    Deterministic Tool: Query ClickHouse to find most frequently utilized filming locations.
    """
    from app.database.clickhouse import get_clickhouse_client
    ch = get_clickhouse_client()
    schedule = list(db_session.schedules.values())[0]
    return ch.query_top_frequent_locations(limit, schedule)


def query_clickhouse_disruption_risk_resources_tool() -> Dict[str, Any]:
    """
    Deterministic Tool: Query ClickHouse analytics for resources most likely to cause schedule disruption.
    """
    from app.database.clickhouse import get_clickhouse_client
    ch = get_clickhouse_client()
    schedule = list(db_session.schedules.values())[0]
    return ch.query_high_risk_disruption_resources(schedule)


def query_clickhouse_disruption_cost_summary_tool() -> Dict[str, Any]:
    """
    Deterministic Tool: Query ClickHouse historical disruption financial impact and daily burn rate savings.
    """
    from app.database.clickhouse import get_clickhouse_client
    ch = get_clickhouse_client()
    schedule = list(db_session.schedules.values())[0]
    return ch.query_total_disruption_cost_summary(schedule)


def query_clickhouse_lowest_impact_scenes_tool() -> Dict[str, Any]:
    """
    Deterministic Tool: Query ClickHouse for indoor cover scenes that can be moved with lowest budget impact.
    """
    from app.database.clickhouse import get_clickhouse_client
    ch = get_clickhouse_client()
    schedule = list(db_session.schedules.values())[0]
    return ch.query_lowest_impact_movable_scenes(schedule)







