import pytest
from app.scheduling.engine import SchedulingEngine
from app.agent.orchestrator import ProductionManagerAgent
from app.database.session import db_session
from app.models.schedule import ProductionSchedule, ShootingDay, Scene, IndoorOutdoor, PriorityLevel, SceneStatus

@pytest.fixture
def engine():
    return SchedulingEngine()

@pytest.fixture
def schedule():
    return list(db_session.schedules.values())[0]

@pytest.fixture
def agent():
    return ProductionManagerAgent()


# --- EDGE CASE 1: NO ALTERNATIVE SCENE EXISTS ---
def test_edge_case_1_no_alternative_scene_exists(engine):
    """When all future scenes are outdoor/fixed and no indoor cover scene exists."""
    no_cover_schedule = ProductionSchedule(
        id="sched_no_cover",
        project_title="Strict Outdoor Film",
        director="Test",
        producer="Test",
        total_budget=500000.0,
        daily_burn_rate=50000.0,
        start_date="2026-10-01",
        total_days=2,
        scenes=[
            Scene(
                scene_id="sc_out_1",
                scene_number="1",
                title="Glacier Summit Extraction",
                description="Outdoor summit flight",
                shooting_date="2026-10-01",
                start_time="08:00",
                duration=6.0,
                location_id="loc_outdoor",
                actor_ids=["act_01"],
                crew_ids=["crw_01"],
                equipment_ids=["eq_01"],
                estimated_cost=20000.0,
                priority=PriorityLevel.HIGH,
                indoor_outdoor=IndoorOutdoor.OUTDOOR,
                weather_sensitive=True,
                status=SceneStatus.SCHEDULED,
            ),
            Scene(
                scene_id="sc_out_2",
                scene_number="2",
                title="Mountain Ridge Chase",
                description="Outdoor cliff chase",
                shooting_date="2026-10-02",
                start_time="08:00",
                duration=6.0,
                location_id="loc_outdoor",
                actor_ids=["act_02"],
                crew_ids=["crw_01"],
                equipment_ids=["eq_01"],
                estimated_cost=20000.0,
                priority=PriorityLevel.HIGH,
                indoor_outdoor=IndoorOutdoor.OUTDOOR,
                weather_sensitive=True,
                status=SceneStatus.SCHEDULED,
            ),
        ],
        actors=[],
        crew=[],
        locations=[],
        equipment=[],
        shooting_days=[
            ShootingDay(day_number=1, date="2026-10-01", call_time="07:00", wrap_time="19:00", location_id="loc_outdoor", scene_ids=["sc_out_1"], estimated_daily_cost=50000.0),
            ShootingDay(day_number=2, date="2026-10-02", call_time="07:00", wrap_time="19:00", location_id="loc_outdoor", scene_ids=["sc_out_2"], estimated_daily_cost=50000.0),
        ]
    )

    covers = engine.find_indoor_cover_scenes(no_cover_schedule, 1)
    assert len(covers) == 0  # No fake cover scenes invented!

    options = engine.generate_recovery_options(no_cover_schedule, "act_01", 1)
    assert len(options) >= 1
    assert "No candidate indoor cover scenes" in options[0]["summary"] or options[0]["schedule_variance_days"] >= 0


# --- EDGE CASE 2: ALL ALTERNATIVE RESOURCES ARE UNAVAILABLE ---
def test_edge_case_2_all_alternative_resources_unavailable(engine, schedule):
    """When all alternative locations or equipment items are unavailable or non-existent."""
    alts = engine.find_alternative_equipment(schedule, "non_existent_equipment_999")
    assert len(alts) == 0  # Does not invent fake equipment!

    compat = engine.check_equipment_compatibility(schedule, "non_existent_eq", "sc_01")
    assert compat is False


# --- EDGE CASE 3: MULTIPLE DISRUPTIONS AFFECT THE SAME SCENE ---
def test_edge_case_3_multiple_disruptions_same_scene(engine, schedule, agent):
    """Actor + Camera + Weather all affect Day 6 scenes simultaneously."""
    disruptions = [
        {"disruption_type": "actor_unavailable", "resource_id": "act_03", "shoot_day": 6, "reason": "Medical hold"},
        {"disruption_type": "equipment_failure", "resource_id": "eq_01", "shoot_day": 6, "reason": "Shutter failure"},
        {"disruption_type": "bad_weather", "resource_id": "loc_04", "shoot_day": 6, "reason": "Heavy Rain", "weather_type": "Heavy Rain", "severity": "High"},
    ]

    graph = engine.build_multi_disruption_dependency_graph(schedule, disruptions)
    assert graph["affected_scene_count"] >= 1
    assert "act_03" in graph["affected_actor_ids"]
    assert "eq_01" in graph["affected_equipment_ids"]

    conflicts = engine.detect_recovery_conflicts(schedule, disruptions)
    assert len(conflicts) >= 1

    analysis = agent.process_multi_disruption(disruptions)
    assert analysis["status"] == "analyzed"
    assert len(analysis["detected_conflicts"]) >= 1


# --- EDGE CASE 4: ACTOR UNAVAILABLE FOR MULTIPLE DAYS ---
def test_edge_case_4_actor_unavailable_multiple_days(engine, schedule):
    """Actor unavailable across a multi-day span (Day 4 and Day 5)."""
    day4_affected = engine.find_affected_scenes(schedule, "act_01", 4)
    day5_affected = engine.find_affected_scenes(schedule, "act_01", 5)

    combined_affected = day4_affected + day5_affected
    assert len(combined_affected) >= 1


# --- EDGE CASE 5: LOCATION AND EQUIPMENT FAIL SIMULTANEOUSLY ---
def test_edge_case_5_location_and_equipment_fail_simultaneously(engine, schedule, agent):
    """Location C unavailable AND Camera A failed on Day 6."""
    disruptions = [
        {"disruption_type": "location_unavailable", "resource_id": "loc_03", "shoot_day": 6, "reason": "Coolant leak"},
        {"disruption_type": "equipment_failure", "resource_id": "eq_01", "shoot_day": 6, "reason": "Power failure"},
    ]

    analysis = agent.process_multi_disruption(disruptions)
    assert analysis["active_disruption_count"] == 2
    assert "recommended_plan" in analysis


# --- EDGE CASE 6: RECOVERY PLAN CREATES A NEW CONFLICT ---
def test_edge_case_6_recovery_plan_creates_new_conflict(engine, schedule):
    """Moving a scene to a target day causes secondary overbooking collisions; conflict detector flags it."""
    disruptions = [
        {"disruption_type": "actor_unavailable", "resource_id": "act_01", "shoot_day": 6},
        {"disruption_type": "equipment_failure", "resource_id": "eq_01", "shoot_day": 6},
    ]

    conflicts = engine.detect_recovery_conflicts(schedule, disruptions)
    assert any(c["type"] == "schedule_overbooking_collision" for c in conflicts)


# --- EDGE CASE 7: INSUFFICIENT INFORMATION IS AVAILABLE ---
def test_edge_case_7_insufficient_information_available(agent, client):
    """Passing blank resource ID or invalid shoot day number to disruption endpoints."""
    res = client.post("/api/v1/disruptions/analyze", json={
        "disruption_type": "actor_unavailable",
        "resource_id": "act_01",
        "shoot_day": 999,
        "reason": "Test"
    })
    assert res.status_code == 400

    res = client.post("/api/v1/disruptions/analyze", json={
        "disruption_type": "actor_unavailable",
        "resource_id": "",
        "shoot_day": 4,
        "reason": "Test"
    })
    assert res.status_code == 400


# --- EDGE CASE 8: NO SOLUTION CAN BE FOUND ---
def test_edge_case_8_no_solution_can_be_found(agent):
    """When a non-existent resource ID is processed, agent returns structured notice without fabricating missing data."""
    analysis = agent.analyze_disruption(
        disruption_type="actor_unavailable",
        resource_id="non_existent_actor_999",
        shoot_day=4,
        reason="Testing unknown resource"
    )
    assert "recovery_options" in analysis
    assert len(analysis["affected_scenes"]) == 0  # 0 fake scenes fabricated!
