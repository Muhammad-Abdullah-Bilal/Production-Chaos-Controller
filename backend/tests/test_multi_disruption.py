import pytest
from app.agent.orchestrator import get_production_manager_agent


def test_multi_disruption_agent_workflow():
    """Test multi-disruption analysis (Chaos Mode) on Day 6 with 3 simultaneous disruptions."""
    agent = get_production_manager_agent()

    disruptions = [
        {"disruption_type": "actor_unavailable", "resource_id": "act_01", "shoot_day": 6, "reason": "Dr. Sarah Mercer unavailable"},
        {"disruption_type": "equipment_failure", "resource_id": "eq_01", "shoot_day": 6, "reason": "RED V-Raptor 8K failure"},
        {"disruption_type": "bad_weather", "resource_id": "loc_03", "shoot_day": 6, "weather_type": "Heavy Rain", "severity": "High", "reason": "Heavy Rain at Glacier Ridge"},
    ]

    res = agent.process_multi_disruption(disruptions)

    assert res["status"] == "analyzed"
    assert res["mode"] == "chaos_mode_multi_disruption"
    assert res["active_disruption_count"] == 3
    assert len(res["affected_scenes"]) > 0
    assert len(res["affected_resources"]) > 0
    assert len(res["detected_conflicts"]) >= 1
    assert len(res["recovery_options"]) >= 3
    assert res["recommended_plan"]["is_recommended"] is True
    assert res["schedule_impact"]["schedule_variance_days"] == 0
    assert "reasoning" in res
    assert len(res["tool_execution_trace"]) >= 5


def test_multi_disruption_api_endpoint(client):
    """Test POST /api/v1/disruptions/multi-analyze endpoint."""
    payload = {
        "disruptions": [
            {"disruption_type": "actor_unavailable", "resource_id": "act_01", "shoot_day": 6, "reason": "John Carter unavailable"},
            {"disruption_type": "equipment_failure", "resource_id": "eq_01", "shoot_day": 6, "reason": "Camera A sensor failed"},
            {"disruption_type": "bad_weather", "resource_id": "loc_03", "shoot_day": 6, "weather_type": "Heavy Rain", "severity": "High", "reason": "Downpour forecast"},
        ]
    }

    response = client.post("/api/v1/disruptions/multi-analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "analyzed"
    assert data["mode"] == "chaos_mode_multi_disruption"
    assert data["active_disruption_count"] == 3
    assert len(data["detected_conflicts"]) >= 1
    assert data["requires_human_approval"] is True
    assert len(data["recovery_options"]) >= 3
