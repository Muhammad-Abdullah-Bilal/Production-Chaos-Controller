import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.clickhouse import get_clickhouse_client
from app.database.session import db_session

client = TestClient(app)


def test_clickhouse_client_diagnostics():
    """Test ClickHouse client connection checker."""
    ch = get_clickhouse_client()
    diag = ch.check_connection()
    assert "status" in diag
    assert "data_source" in diag
    assert diag["mcp_enabled"] is True


def test_clickhouse_all_6_analytics_queries():
    """Test all 6 canonical production analytics queries with automatic fallback verification."""
    ch = get_clickhouse_client()
    schedule = list(db_session.schedules.values())[0]

    # 1. Which scenes depend on a specific actor?
    q1 = ch.query_scenes_by_actor("act_01", schedule)
    assert q1["query"] == "scenes_by_actor"
    assert q1["count"] > 0
    assert "scenes" in q1

    # 2. Which scenes use a specific equipment item?
    q2 = ch.query_scenes_by_equipment("eq_01", schedule)
    assert q2["query"] == "scenes_by_equipment"
    assert q2["count"] > 0
    assert "scenes" in q2

    # 3. Which locations are used most frequently?
    q3 = ch.query_top_frequent_locations(5, schedule)
    assert q3["query"] == "top_frequent_locations"
    assert len(q3["locations"]) > 0

    # 4. What resources are most likely to cause schedule disruption?
    q4 = ch.query_high_risk_disruption_resources(schedule)
    assert q4["query"] == "high_risk_disruption_resources"
    assert len(q4["risk_resources"]) > 0

    # 5. What is the estimated cost of previous disruptions?
    q5 = ch.query_total_disruption_cost_summary(schedule)
    assert q5["query"] == "total_disruption_cost_summary"
    assert "by_type" in q5

    # 6. Which scenes can be moved with the lowest impact?
    q6 = ch.query_lowest_impact_movable_scenes(schedule)
    assert q6["query"] == "lowest_impact_movable_scenes"
    assert "movable_scenes" in q6


def test_clickhouse_mcp_manifest_and_execution():
    """Test official MCP manifest export and MCP tool execution."""
    ch = get_clickhouse_client()
    manifest = ch.get_mcp_manifest()
    assert manifest["server"] == "clickhouse-mcp-server"
    assert len(manifest["capabilities"]["tools"]) == 6

    # Execute MCP Tool
    schedule = list(db_session.schedules.values())[0]
    mcp_res = ch.execute_mcp_tool("clickhouse_scenes_by_actor", {"actor_id": "act_01"}, schedule)
    assert mcp_res["query"] == "scenes_by_actor"
    assert mcp_res["count"] > 0


def test_clickhouse_api_endpoints():
    """Test ClickHouse REST and MCP endpoints."""
    # Status endpoint
    status_res = client.get("/api/v1/analytics/clickhouse/status")
    assert status_res.status_code == 200
    assert "data_source" in status_res.json()

    # Analytics query endpoint
    query_res = client.post(
        "/api/v1/analytics/clickhouse/query",
        json={"query_name": "high_risk_disruption_resources", "params": {}},
    )
    assert query_res.status_code == 200
    assert query_res.json()["query"] == "high_risk_disruption_resources"

    # MCP Manifest endpoint
    mcp_manifest_res = client.get("/api/v1/mcp/clickhouse")
    assert mcp_manifest_res.status_code == 200
    assert "capabilities" in mcp_manifest_res.json()

    # MCP Execute endpoint
    mcp_exec_res = client.post(
        "/api/v1/mcp/clickhouse/execute",
        json={"name": "clickhouse_total_disruption_cost_summary", "arguments": {}},
    )
    assert mcp_exec_res.status_code == 200
    assert mcp_exec_res.json()["query"] == "total_disruption_cost_summary"
