# ClickHouse Integration & MCP Setup Guide — Production Chaos Controller

This guide details the architecture, schema design, Model Context Protocol (MCP) tool integration, environment configuration, local development instructions, and production deployment guidelines for **ClickHouse** integration in **Production Chaos Controller**.

---

## 1. Overview & Architecture

Production Chaos Controller integrates **ClickHouse** as its official high-throughput analytics engine and MCP tool provider. The integration enables the central `ProductionManagerAgent` and line producers to query production dependencies, historical disruption trends, location utilization, and recovery cost variances in real-time.

```
┌─────────────────────────────────────────────────────────┐
│              Production Manager AI Agent                │
│             (Google Gemini 2.5 Orchestrator)            │
└────────────────────────────┬────────────────────────────┘
                             │
     ┌───────────────────────┴───────────────────────┐
     ▼                                               ▼
┌───────────────────────────┐           ┌───────────────────────────┐
│   Official ClickHouse     │           │   Local In-Memory Cache   │
│   Analytics & MCP Server  │◄─────────►│     (db_session)        │
│    (MergeTree Engine)     │           │   (Automatic Fallback)    │
└───────────────────────────┘           └───────────────────────────┘
```

### Zero-Downtime Fallback Architecture
If the ClickHouse server is unreachable or disabled (`CLICKHOUSE_ENABLED=false`), the system automatically routes queries to in-memory datasets while explicitly setting `"data_source": "local_fallback"`. When ClickHouse is active, queries run directly over ClickHouse tables and set `"data_source": "clickhouse"`.

---

## 2. ClickHouse Setup & Installation

### Option A: Local Docker Setup (Recommended for Development)
To launch a ClickHouse server locally using Docker:

```bash
docker run -d \
  --name clickhouse-server \
  -p 8123:8123 \
  -p 9000:9000 \
  --ulimit nofile=262144:262144 \
  clickhouse/clickhouse-server
```

Verify connection:
```bash
curl "http://localhost:8123/?query=SELECT%20version()"
```

### Option B: ClickHouse Cloud Setup (Production)
1. Provision a ClickHouse Cloud service at [clickhouse.com](https://clickhouse.com/).
2. Obtain your service host (`https://xxx.clickhouse.cloud`), port (`8443`), username (`default`), and password.
3. Configure environment variables accordingly.

---

## 3. Environment Variables

Add or update the following variables in `backend/.env`:

```ini
# ClickHouse Configuration
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=
CLICKHOUSE_DB=production_chaos
CLICKHOUSE_SECURE=false
CLICKHOUSE_ENABLED=true
```

---

## 4. Schema & 10 Production Tables (`MergeTree`)

All tables are automatically provisioned on startup in database `production_chaos` using ClickHouse `MergeTree` engines:

### 1. `scenes`
```sql
CREATE TABLE IF NOT EXISTS scenes (
    scene_id String,
    scene_number Int32,
    title String,
    description String,
    shooting_date String,
    start_time String,
    duration Int32,
    location_id String,
    actor_ids Array(String),
    crew_ids Array(String),
    equipment_ids Array(String),
    estimated_cost Float64,
    priority String,
    indoor_outdoor String,
    weather_sensitive UInt8,
    status String
) ENGINE = MergeTree() ORDER BY scene_id;
```

### 2. `shooting_schedules`
```sql
CREATE TABLE IF NOT EXISTS shooting_schedules (
    shoot_day Int32,
    date String,
    location_ids Array(String),
    scene_ids Array(String),
    actor_ids Array(String),
    crew_ids Array(String),
    equipment_ids Array(String),
    daily_cost Float64,
    status String
) ENGINE = MergeTree() ORDER BY shoot_day;
```

### 3. `actors`
```sql
CREATE TABLE IF NOT EXISTS actors (
    actor_id String,
    name String,
    character_name String,
    daily_rate Float64,
    is_lead UInt8,
    max_work_hours_per_day Int32,
    availability_status String
) ENGINE = MergeTree() ORDER BY actor_id;
```

### 4. `crew`
```sql
CREATE TABLE IF NOT EXISTS crew (
    crew_id String,
    name String,
    role String,
    department String,
    daily_rate Float64,
    shift_start_time String,
    shift_duration_hours Int32,
    availability_status String
) ENGINE = MergeTree() ORDER BY crew_id;
```

### 5. `equipment`
```sql
CREATE TABLE IF NOT EXISTS equipment (
    equipment_id String,
    name String,
    category String,
    daily_rental_cost Float64,
    location_id String,
    is_critical UInt8,
    backup_equipment_id String,
    status String
) ENGINE = MergeTree() ORDER BY equipment_id;
```

### 6. `locations`
```sql
CREATE TABLE IF NOT EXISTS locations (
    location_id String,
    name String,
    indoor_outdoor String,
    address String,
    daily_rate Float64,
    weather_vulnerable UInt8,
    status String
) ENGINE = MergeTree() ORDER BY location_id;
```

### 7. `production_events`
```sql
CREATE TABLE IF NOT EXISTS production_events (
    event_id String,
    event_type String,
    timestamp String,
    description String,
    severity String,
    metadata_json String
) ENGINE = MergeTree() ORDER BY event_id;
```

### 8. `disruption_history`
```sql
CREATE TABLE IF NOT EXISTS disruption_history (
    disruption_id String,
    disruption_type String,
    resource_id String,
    shoot_day Int32,
    reason String,
    severity String,
    cost_impact_usd Float64,
    schedule_delay_days Int32,
    created_at String
) ENGINE = MergeTree() ORDER BY disruption_id;
```

### 9. `recovery_plans`
```sql
CREATE TABLE IF NOT EXISTS recovery_plans (
    plan_id String,
    disruption_id String,
    title String,
    strategy String,
    cost_variance_usd Float64,
    schedule_variance_days Int32,
    is_recommended UInt8,
    is_approved UInt8,
    approved_by String,
    reasoning String,
    created_at String
) ENGINE = MergeTree() ORDER BY plan_id;
```

### 10. `cost_records`
```sql
CREATE TABLE IF NOT EXISTS cost_records (
    record_id String,
    category String,
    amount_usd Float64,
    description String,
    shoot_day Int32,
    timestamp String
) ENGINE = MergeTree() ORDER BY record_id;
```

---

## 5. Official Production Analytics Queries

The system exposes 6 canonical analytical queries over ClickHouse:

| Query Name | Description | Example SQL |
| :--- | :--- | :--- |
| `scenes_by_actor` | Scenes dependent on a specific actor | `SELECT * FROM scenes WHERE has(actor_ids, 'act_01')` |
| `scenes_by_equipment` | Scenes utilizing a specific equipment asset | `SELECT * FROM scenes WHERE has(equipment_ids, 'eq_01')` |
| `top_frequent_locations` | Most frequently utilized filming locations | `SELECT l.name, count(s.scene_id) FROM locations l LEFT JOIN scenes s ON l.location_id = s.location_id GROUP BY l.name ORDER BY count(s.scene_id) DESC` |
| `high_risk_disruption_resources` | Resources most likely to cause schedule delay | `SELECT resource_id, disruption_type, count() FROM disruption_history GROUP BY resource_id, disruption_type ORDER BY count() DESC` |
| `total_disruption_cost_summary` | Historical disruption cost & burn rate savings | `SELECT disruption_type, sum(cost_impact_usd) FROM disruption_history GROUP BY disruption_type` |
| `lowest_impact_movable_scenes` | Indoor cover scenes movable with minimal cost | `SELECT * FROM scenes WHERE indoor_outdoor = 'indoor' AND priority != 'high' ORDER BY estimated_cost ASC` |

---

## 6. Official MCP (Model Context Protocol) Integration

### Manifest Export Endpoint
`GET /api/v1/mcp/clickhouse`

Returns standardized MCP tool definitions:
```json
{
  "server": "clickhouse-mcp-server",
  "version": "1.0.0",
  "capabilities": {
    "tools": [
      {
        "name": "clickhouse_scenes_by_actor",
        "description": "Query ClickHouse for film scenes depending on a specific actor",
        "parameters": {
          "type": "object",
          "properties": { "actor_id": { "type": "string" } },
          "required": ["actor_id"]
        }
      },
      {
        "name": "clickhouse_high_risk_disruption_resources",
        "description": "Query ClickHouse analytics for resources with highest disruption risk",
        "parameters": { "type": "object", "properties": {} }
      }
    ]
  }
}
```

### Tool Execution Endpoint
`POST /api/v1/mcp/clickhouse/execute`

Payload:
```json
{
  "name": "clickhouse_scenes_by_actor",
  "arguments": { "actor_id": "act_01" }
}
```

---

## 7. Local Development & Verification Commands

### Run Backend Pytest Suite
```bash
cd backend
uv run pytest
```

### Sync Local Memory Data to ClickHouse
```bash
curl -X POST "http://localhost:8000/api/v1/analytics/clickhouse/sync"
```

### Check Connection Diagnostic Status
```bash
curl "http://localhost:8000/api/v1/analytics/clickhouse/status"
```

### Run Frontend Production Build
```bash
cd frontend
npm run build
```

---

## 8. Deployment Guidelines

1. **ClickHouse Cloud / Managed Service**: Deploy ClickHouse Cloud and update `CLICKHOUSE_HOST`, `CLICKHOUSE_PORT=8443`, `CLICKHOUSE_SECURE=true`, `CLICKHOUSE_PASSWORD` in your secret manager.
2. **Database Migration / Auto-Sync**: The backend auto-creates schema tables on boot via `ClickHouseClient.init_tables()`.
3. **Monitoring & Auditing**: Inspect backend logs for `ClickHouse connection successfully established` or `Using local memory fallback` messages.
