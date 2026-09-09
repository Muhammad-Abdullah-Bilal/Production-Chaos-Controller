def test_get_schedule(client):
    response = client.get("/api/v1/schedule")
    assert response.status_code == 200
    data = response.json()
    assert data["project_title"] == "The Last Signal"
    assert len(data["scenes"]) == 20
    assert len(data["actors"]) == 8
    assert len(data["crew"]) == 10
    assert len(data["locations"]) == 4
    assert len(data["equipment"]) == 5
    assert len(data["shooting_days"]) == 10


def test_production_data_layer_apis(client):
    """Test all production data layer endpoints requested by prompt."""
    res_prod = client.get("/api/production")
    assert res_prod.status_code == 200
    assert res_prod.json()["project_title"] == "The Last Signal"

    res_scenes = client.get("/api/scenes")
    assert res_scenes.status_code == 200
    assert len(res_scenes.json()) == 20

    res_actors = client.get("/api/actors")
    assert res_actors.status_code == 200
    assert len(res_actors.json()) == 8

    res_crew = client.get("/api/crew")
    assert res_crew.status_code == 200
    assert len(res_crew.json()) == 10

    res_locations = client.get("/api/locations")
    assert res_locations.status_code == 200
    assert len(res_locations.json()) == 4

    res_equipment = client.get("/api/equipment")
    assert res_equipment.status_code == 200
    assert len(res_equipment.json()) == 5

    res_sched = client.get("/api/schedule")
    assert res_sched.status_code == 200
    assert len(res_sched.json()) == 10


def test_actor_disruption_scenario(client):
    """Test POST /api/disruptions/actor-unavailable for John Carter / Sarah Mercer scenario on Day 4."""
    payload = {
        "actor_id": "act_01",
        "shoot_day": 4,
        "reason": "Dr. Sarah Mercer unavailable on Day 4 due to emergency medical hold.",
    }
    response = client.post("/api/disruptions/actor-unavailable", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["disruption"]["actor_id"] == "act_01"
    assert data["disruption"]["shoot_day"] == 4
    assert len(data["affected_scenes"]) > 0
    assert len(data["recovery_options"]) >= 3
    assert data["recommended_plan"]["is_recommended"] is True
    assert "reasoning" in data
    assert "schedule_impact" in data
    assert "cost_impact" in data
    assert "confidence" in data


def test_equipment_failure_scenario(client):
    """Test POST /api/disruptions/equipment-failure for Camera A / RED V-Raptor 8K failure on Day 5."""
    payload = {
        "equipment_id": "eq_01",
        "shoot_day": 5,
        "reason": "RED V-Raptor 8K primary sensor shutter breakdown on Day 5.",
    }
    response = client.post("/api/disruptions/equipment-failure", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["problem"].startswith("Equipment failure:")
    assert data["disruption"]["equipment_id"] == "eq_01"
    assert data["disruption"]["shoot_day"] == 5
    assert len(data["affected"]["scenes"]) > 0
    assert len(data["affected"]["dates"]) > 0
    assert len(data["affected"]["crew"]) > 0
    assert len(data["affected"]["locations"]) > 0
    assert len(data["recovery_options"]) >= 3
    assert data["recommended_plan"]["is_recommended"] is True
    assert "reasoning" in data
    assert "schedule_impact" in data
    assert "cost_impact" in data


def test_location_unavailable_scenario(client):
    """Test POST /api/disruptions/location-unavailable for Sub-Zero Quantum Vault / City Hospital on Day 6."""
    payload = {
        "location_id": "loc_03",
        "shoot_day": 6,
        "reason": "Sub-Zero Quantum Vault / City Hospital unavailable on Day 6 due to emergency lockdown.",
    }
    response = client.post("/api/disruptions/location-unavailable", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["problem"].startswith("Location unavailable:")
    assert data["disruption"]["location_id"] == "loc_03"
    assert data["disruption"]["shoot_day"] == 6
    assert len(data["affected"]["scenes"]) > 0
    assert len(data["affected"]["actors"]) > 0
    assert len(data["affected"]["crew"]) > 0
    assert len(data["alternative_locations"]) > 0
    assert len(data["recovery_options"]) >= 3
    assert data["recommended_plan"]["is_recommended"] is True
    assert "reasoning" in data
    assert "schedule_impact" in data
    assert "cost_impact" in data


def test_weather_disruption_scenario(client):
    """Test POST /api/disruptions/bad-weather for Heavy Rain forecast on Day 7."""
    payload = {
        "weather_type": "Heavy Rain",
        "severity": "High",
        "shoot_day": 7,
        "reason": "Severe torrential rain forecast on Day 7.",
    }
    response = client.post("/api/disruptions/bad-weather", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["problem"].startswith("Weather disruption:")
    assert data["disruption"]["weather_type"] == "Heavy Rain"
    assert data["disruption"]["shoot_day"] == 7
    assert len(data["affected"]["scenes"]) > 0
    assert len(data["alternative_indoor_scenes"]) > 0
    assert len(data["alternative_dates"]) > 0
    assert len(data["recovery_options"]) >= 3
    assert data["recommended_plan"]["is_recommended"] is True
    assert "weather_risk" in data
    assert "reasoning" in data
    assert "schedule_impact" in data
    assert "cost_impact" in data


def test_crew_disruption_scenario(client):
    """Test POST /api/disruptions/crew-unavailable for Director of Photography Claire Delacroix on Day 5."""
    payload = {
        "crew_id": "crw_02",
        "shoot_day": 5,
        "reason": "Director of Photography Claire Delacroix suddenly unavailable on Day 5.",
    }
    response = client.post("/api/disruptions/crew-unavailable", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["problem"].startswith("Crew member unavailable:")
    assert data["disruption"]["crew_id"] == "crw_02"
    assert data["disruption"]["shoot_day"] == 5
    assert len(data["affected"]["scenes"]) > 0
    assert len(data["qualified_replacements"]) > 0
    assert len(data["recovery_options"]) >= 3
    assert data["recommended_plan"]["is_recommended"] is True
    assert "reasoning" in data
    assert "schedule_impact" in data
    assert "cost_impact" in data


def test_logistics_disruption_scenario(client):
    """Test POST /api/disruptions/logistics-delay for equipment transport vehicle breakdown on Day 8."""
    payload = {
        "vehicle_id": "veh_01",
        "shoot_day": 8,
        "delay_hours": 2,
        "reason": "Equipment transport vehicle breakdown on mountain highway on Day 8.",
    }
    response = client.post("/api/disruptions/logistics-delay", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["problem"].startswith("Transportation breakdown:")
    assert data["disruption"]["vehicle_id"] == "veh_01"
    assert data["disruption"]["shoot_day"] == 8
    assert len(data["affected"]["scenes"]) > 0
    assert len(data["recovery_options"]) >= 3
    assert data["recommended_plan"]["is_recommended"] is True
    assert "dispatch_feasibility" in data
    assert "reasoning" in data
    assert "schedule_impact" in data
    assert "cost_impact" in data


def test_validate_schedule(client):
    response = client.get("/api/v1/schedule/validate")
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True




