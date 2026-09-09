import pytest
from app.scheduling.engine import SchedulingEngine
from app.agent.orchestrator import ProductionManagerAgent
from app.database.session import db_session

@pytest.fixture
def engine():
    return SchedulingEngine()

@pytest.fixture
def schedule():
    return list(db_session.schedules.values())[0]

@pytest.fixture
def agent():
    return ProductionManagerAgent()


# --- SCENARIO 1: ACTOR UNAVAILABLE ---
def test_actor_unavailable_scenario(engine, schedule, client):
    actor_id = "act_01"  # Dr. Sarah Mercer
    shoot_day = 4

    # 1. Affected scene detection
    affected = engine.find_affected_scenes(schedule, actor_id, shoot_day)
    assert len(affected) > 0
    assert any(actor_id in sc.actor_ids for sc in affected)

    # 2. Future affected scenes
    future_affected = engine.find_future_affected_scenes(schedule, actor_id, shoot_day)
    assert isinstance(future_affected, list)

    # 3. Availability checks
    is_loc_avail = engine.check_location_availability(schedule, "loc_02", shoot_day)
    assert is_loc_avail is True

    # 4. Cost and schedule calculations
    sched_impact = engine.calculate_schedule_impact(10, 10)
    assert sched_impact["schedule_variance_days"] == 0

    cost_impact = engine.calculate_cost_impact(affected, 0, schedule.daily_burn_rate)
    assert cost_impact["total_cost_variance_usd"] >= 0

    # 5. Recovery options ranking
    options = engine.generate_recovery_options(schedule, actor_id, shoot_day)
    assert len(options) >= 2
    recommended = next(o for o in options if o["is_recommended"])
    assert recommended["schedule_variance_days"] == 0

    # 6. API Endpoint test
    res = client.post("/api/v1/disruptions/actor-unavailable", json={
        "actor_id": actor_id,
        "shoot_day": shoot_day,
        "reason": "Emergency medical hold"
    })
    assert res.status_code == 200
    data = res.json()
    assert "recovery_options" in data
    assert "recommended_plan" in data


# --- SCENARIO 2: EQUIPMENT FAILURE ---
def test_equipment_failure_scenario(engine, schedule, client):
    equipment_id = "eq_01"  # RED V-Raptor 8K
    shoot_day = 5

    # 1. Equipment dependencies
    deps = engine.find_equipment_dependencies(schedule, equipment_id, shoot_day)
    assert len(deps) > 0

    # 2. Alternative equipment lookup
    alts = engine.find_alternative_equipment(schedule, equipment_id)
    assert len(alts) >= 0

    # 3. Compatibility check
    is_compat = engine.check_equipment_compatibility(schedule, equipment_id, "sc_09")
    assert is_compat is True

    # 4. Crew operator qualification check
    all_crew_ids = [c.crew_id for c in schedule.crew]
    has_operator = engine.check_crew_for_equipment(schedule, equipment_id, all_crew_ids)
    assert has_operator is True

    # 5. Impact calculation & options
    options = engine.generate_equipment_recovery_options(schedule, equipment_id, shoot_day)
    assert len(options) >= 2
    rec = next(o for o in options if o["is_recommended"])
    assert rec["cost_variance_usd"] < 85000.0

    # 6. API Endpoint test
    res = client.post("/api/v1/disruptions/equipment-failure", json={
        "equipment_id": equipment_id,
        "shoot_day": shoot_day,
        "reason": "Sensor shutter failure"
    })
    assert res.status_code == 200
    assert "recommended_plan" in res.json()


# --- SCENARIO 3: LOCATION UNAVAILABLE ---
def test_location_unavailable_scenario(engine, schedule, client):
    location_id = "loc_03"  # Sub-Zero Quantum Vault
    shoot_day = 6

    # 1. Location dependencies
    deps = engine.find_location_dependencies(schedule, location_id, shoot_day)
    assert len(deps) > 0

    # 2. Alternative approved locations
    alts = engine.find_alternative_locations(schedule, location_id)
    assert len(alts) > 0

    # 3. Location requirements check
    alt_loc_id = alts[0].location_id if hasattr(alts[0], "location_id") else alts[0]["location_id"]
    reqs_ok = engine.check_location_requirements(schedule, alt_loc_id, deps[0].scene_id)
    assert reqs_ok["compatible"] is True

    # 4. Options generation & ranking
    options = engine.generate_location_recovery_options(schedule, location_id, shoot_day)
    assert len(options) >= 2
    assert options[0]["is_recommended"] is True

    # 5. API Endpoint test
    res = client.post("/api/v1/disruptions/location-unavailable", json={
        "location_id": location_id,
        "shoot_day": shoot_day,
        "reason": "Emergency facility lockdown"
    })
    assert res.status_code == 200
    assert res.json()["disruption"]["type"] == "location_unavailable"


# --- SCENARIO 4: BAD WEATHER ---
def test_bad_weather_scenario(engine, schedule, client):
    shoot_day = 7

    # 1. Weather affected outdoor scenes
    affected = engine.find_weather_affected_scenes(schedule, shoot_day, "Heavy Rain", "High")
    assert len(affected) > 0

    # 2. Indoor cover scenes lookup
    indoor_covers = engine.find_indoor_cover_scenes(schedule, shoot_day)
    assert len(indoor_covers) > 0

    # 3. Alternative outdoor dates lookup
    affected_ids = [s.scene_id for s in affected]
    alt_dates = engine.find_alternative_outdoor_dates(schedule, affected_ids, shoot_day)
    assert len(alt_dates) > 0

    # 4. Options generation
    options = engine.generate_weather_recovery_options(schedule, "Heavy Rain", "High", shoot_day)
    assert len(options) >= 2

    # 5. API Endpoint test
    res = client.post("/api/v1/disruptions/bad-weather", json={
        "weather_type": "Heavy Rain",
        "severity": "High",
        "shoot_day": shoot_day,
        "reason": "Torrential downpour"
    })
    assert res.status_code == 200
    assert res.json()["recommended_plan"]["schedule_variance_days"] == 0


# --- SCENARIO 5: CREW UNAVAILABLE ---
def test_crew_unavailable_scenario(engine, schedule, client):
    crew_id = "crw_02"  # Claire Delacroix - DP
    shoot_day = 5

    # 1. Crew dependencies
    deps = engine.find_crew_dependencies(schedule, crew_id, shoot_day)
    assert len(deps) > 0

    # 2. Qualified replacement crew search
    replacements = engine.find_qualified_replacement_crew(schedule, crew_id)
    assert len(replacements) > 0

    # 3. Crew schedule check
    avail = engine.check_crew_schedule(schedule, replacements[0]["crew_id"], shoot_day)
    assert avail["is_booked"] is False

    # 4. Recovery options
    options = engine.generate_crew_recovery_options(schedule, crew_id, shoot_day)
    assert len(options) >= 2

    # 5. API Endpoint test
    res = client.post("/api/v1/disruptions/crew-unavailable", json={
        "crew_id": crew_id,
        "shoot_day": shoot_day,
        "reason": "Emergency medical hold"
    })
    assert res.status_code == 200
    assert "qualified_replacements" in res.json()


# --- SCENARIO 6: TRANSPORTATION / LOGISTICS BREAKDOWN ---
def test_logistics_breakdown_scenario(engine, schedule, client):
    vehicle_id = "veh_01"
    shoot_day = 8

    # 1. Logistics dependencies
    deps = engine.find_logistics_dependencies(schedule, vehicle_id, shoot_day)
    assert len(deps) > 0

    # 2. Vehicle dispatch feasibility
    dispatch = engine.check_vehicle_dispatch_feasibility(schedule, vehicle_id, shoot_day)
    assert dispatch["hot_shot_dispatch_available"] is True

    # 3. Logistics recovery options
    options = engine.generate_logistics_recovery_options(schedule, vehicle_id, shoot_day, 2)
    assert len(options) >= 2

    # 4. API Endpoint test
    res = client.post("/api/v1/disruptions/logistics-delay", json={
        "vehicle_id": vehicle_id,
        "shoot_day": shoot_day,
        "delay_hours": 2,
        "reason": "Transmission breakdown on mountain highway"
    })
    assert res.status_code == 200
    assert res.json()["dispatch_feasibility"]["backup_transport_eta_hours"] > 0
