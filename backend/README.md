# Production Chaos Controller - Backend

Production-grade FastAPI backend for the AI-powered film production disruption management system.

## Architecture

- **FastAPI**: Modern, asynchronous REST API with automatic OpenAPI documentation.
- **uv**: Ultra-fast Python package and project manager.
- **Pydantic v2**: Type validation and settings management.
- **Agent Orchestrator**: `ProductionManagerAgent` powered by Google Gemini 2.0 Flash (`google-genai` SDK) & Google Cloud Agent Builder / ADK agent pattern.
- **Deterministic Tools**: 20+ discrete scheduling, availability, conflict detection, and cost impact calculation tools.
- **ClickHouse Integration**: Official `clickhouse-connect` integration, 10 `MergeTree` tables, 6 canonical production queries, and ClickHouse MCP server (`/api/v1/mcp/clickhouse`).

## Folder Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── router.py           # Master API router
│   │   └── v1/
│   │       ├── health.py       # Comprehensive health & subsystem check
│   │       ├── schedule.py     # Production schedule endpoints
│   │       ├── disruptions.py  # Disruption reporting & recovery approval
│   │       └── clickhouse.py   # ClickHouse analytics & MCP tool server
│   ├── config/
│   │   └── settings.py         # Pydantic Settings (.env configuration)
│   ├── models/
│   │   ├── schedule.py         # Scene, Resource, ShootDay domain models
│   │   ├── disruption.py       # Disruption events and types
│   │   └── recovery.py         # Recovery plans, impacts, and approvals
│   ├── services/
│   │   └── schedule_service.py # Business logic service coordination
│   ├── scheduling/
│   │   └── engine.py           # Deterministic schedule integrity & conflict detector
│   ├── agent/
│   │   └── orchestrator.py     # ProductionManagerAgent & Gemini 2.0 Flash client
│   ├── tools/
│   │   └── production_tools.py # Deterministic application tools
│   ├── database/
│   │   ├── session.py          # In-memory repository with realistic film seed data
│   │   └── clickhouse.py       # ClickHouse adapter & MCP manifest
│   └── main.py                 # FastAPI app entrypoint with CORS & lifespan
├── tests/
│   ├── conftest.py                     # TestClient fixtures
│   ├── test_health.py                  # Health check endpoint tests
│   ├── test_schedule_api.py            # Schedule & disruption conflict detection tests
│   ├── test_disruption_scenarios.py    # Unit & integration tests for all 6 disruption types
│   ├── test_edge_cases.py              # 8 explicit edge case test suites
│   ├── test_multi_disruption.py        # Chaos Mode multi-disruption collision tests
│   ├── test_production_manager_agent.py # Agent tool calling & multi-step execution trace
│   └── test_clickhouse_integration.py  # ClickHouse queries & MCP endpoint tests
├── .env.example                        # Documented configuration template
├── pyproject.toml                      # uv dependencies & metadata
└── README.md
```

## Running the Backend Independently

### Prerequisites
- Python >= 3.12
- `uv` installed (`https://docs.astral.sh/uv/`)

### Setup & Run

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   ```

3. **Start the development server:**
   ```bash
   uv run uvicorn app.main:app --reload --port 8000
   ```

4. **Verify Health Endpoint:**
   - Health Check: `http://localhost:8000/health` or `http://localhost:8000/api/v1/health`
   - Interactive Docs: `http://localhost:8000/docs`

5. **Run Tests (34 Passed):**
   ```bash
   uv run pytest
   ```

