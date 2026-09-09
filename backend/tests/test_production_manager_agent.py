import pytest
from app.agent.orchestrator import get_production_manager_agent


def test_production_manager_agent_workflow():
    """Test central ProductionManagerAgent across all 6 supported disruption scenarios."""
    agent = get_production_manager_agent()

    scenarios = [
        ("actor_unavailable", "act_01", 4, "Dr. Sarah Mercer medical hold"),
        ("equipment_failure", "eq_01", 5, "RED V-Raptor sensor failure"),
        ("location_unavailable", "loc_03", 6, "Quantum Vault emergency maintenance"),
        ("bad_weather", "glacier_ridge", 7, "Heavy Rain downpour"),
        ("crew_unavailable", "crw_02", 5, "Director of Photography Claire Delacroix unavailable"),
        ("logistics_failure", "veh_01", 8, "Camera & Grip transport breakdown"),
    ]

    for dis_type, res_id, day, reason in scenarios:
        res = agent.analyze_disruption(
            disruption_type=dis_type,
            resource_id=res_id,
            shoot_day=day,
            reason=reason,
        )

        assert res["status"] == "analyzed"
        assert res["disruption"]["type"] == dis_type
        assert res["disruption"]["shoot_day"] == day
        assert isinstance(res["affected_scenes"], list)
        assert isinstance(res["affected_resources"], list)
        assert len(res["recovery_options"]) >= 3
        assert res["recommended_plan"]["is_recommended"] is True
        assert "reasoning" in res
        assert "schedule_impact" in res
        assert "cost_impact" in res
        assert res["requires_human_approval"] is True

        # Verify deterministic tool execution trace
        trace = res["tool_execution_trace"]
        assert isinstance(trace, list)
        assert len(trace) >= 6
        tool_names = [t["tool"] for t in trace]
        assert "get_production_schedule" in tool_names
        assert "find_affected_scenes" in tool_names
        assert "generate_recovery_options" in tool_names


def test_production_manager_agent_api_endpoint(client):
    """Test POST /api/v1/disruptions/analyze endpoint."""
    payload = {
        "disruption_type": "actor_unavailable",
        "resource_id": "act_01",
        "shoot_day": 4,
        "reason": "Dr. Sarah Mercer contractually unavailable on Day 4.",
    }
    response = client.post("/api/v1/disruptions/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "analyzed"
    assert data["disruption"]["type"] == "actor_unavailable"
    assert data["disruption"]["resource_id"] == "act_01"
    assert data["requires_human_approval"] is True
    assert len(data["tool_execution_trace"]) >= 6
