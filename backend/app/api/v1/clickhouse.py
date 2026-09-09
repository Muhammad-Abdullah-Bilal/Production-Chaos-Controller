from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.database.clickhouse import get_clickhouse_client
from app.database.session import db_session

router = APIRouter()


class ClickHouseQueryRequest(BaseModel):
    query_name: str = Field(..., description="Query name: scenes_by_actor, scenes_by_equipment, top_frequent_locations, high_risk_disruption_resources, total_disruption_cost_summary, lowest_impact_movable_scenes")
    params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Query parameters e.g. actor_id, equipment_id, limit")


class MCPExecuteRequest(BaseModel):
    name: str = Field(..., description="MCP Tool name e.g. clickhouse_scenes_by_actor")
    arguments: Optional[Dict[str, Any]] = Field(default_factory=dict, description="MCP Tool arguments")


@router.get("/analytics/clickhouse/status")
def get_clickhouse_status() -> Dict[str, Any]:
    """Check connectivity and data source status of ClickHouse cluster."""
    ch = get_clickhouse_client()
    return ch.check_connection()


@router.post("/analytics/clickhouse/sync")
def sync_clickhouse_data() -> Dict[str, Any]:
    """Sync/seed current production schedule and entities from memory into ClickHouse tables."""
    ch = get_clickhouse_client()
    schedule = list(db_session.schedules.values())[0]
    return ch.sync_from_memory(schedule)


@router.post("/analytics/clickhouse/query")
def run_clickhouse_analytics_query(request: ClickHouseQueryRequest) -> Dict[str, Any]:
    """
    Execute one of the 6 canonical production analytics queries over ClickHouse (with local fallback).
    """
    ch = get_clickhouse_client()
    schedule = list(db_session.schedules.values())[0]
    params = request.params or {}

    if request.query_name == "scenes_by_actor":
        return ch.query_scenes_by_actor(params.get("actor_id", "act_01"), schedule)
    elif request.query_name == "scenes_by_equipment":
        return ch.query_scenes_by_equipment(params.get("equipment_id", "eq_01"), schedule)
    elif request.query_name == "top_frequent_locations":
        return ch.query_top_frequent_locations(int(params.get("limit", 5)), schedule)
    elif request.query_name == "high_risk_disruption_resources":
        return ch.query_high_risk_disruption_resources(schedule)
    elif request.query_name == "total_disruption_cost_summary":
        return ch.query_total_disruption_cost_summary(schedule)
    elif request.query_name == "lowest_impact_movable_scenes":
        return ch.query_lowest_impact_movable_scenes(schedule)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported ClickHouse query name: {request.query_name}")


@router.get("/mcp/clickhouse")
def get_mcp_clickhouse_manifest() -> Dict[str, Any]:
    """
    Export official MCP (Model Context Protocol) tool definitions for ClickHouse integration.
    Allows Gemini, Agent Development Kit, and partner MCP hosts to discover available tools.
    """
    ch = get_clickhouse_client()
    return ch.get_mcp_manifest()


@router.post("/mcp/clickhouse/execute")
def execute_mcp_clickhouse_tool(request: MCPExecuteRequest) -> Dict[str, Any]:
    """
    Official MCP tool execution handler for ClickHouse.
    Executes specified MCP tool against ClickHouse database layer.
    """
    ch = get_clickhouse_client()
    schedule = list(db_session.schedules.values())[0]
    return ch.execute_mcp_tool(request.name, request.arguments or {}, schedule)
