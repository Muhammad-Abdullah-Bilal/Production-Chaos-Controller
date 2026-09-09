# 🎬 Production Chaos Controller

> **AI-Powered Autonomous Disruption Management & Recovery System for Film & Television Production**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.141.1-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15.1.0-000000?style=flat-square&logo=next.js)](https://nextjs.org/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-2.0--Flash-4285F4?style=flat-square&logo=google)](https://ai.google.dev/)
[![ClickHouse](https://img.shields.io/badge/ClickHouse-MCP%20Integration-FFCC00?style=flat-square&logo=clickhouse)](https://clickhouse.com/)
[![uv](https://img.shields.io/badge/uv-Package%20Manager-DE5C8E?style=flat-square)](https://docs.astral.sh/uv/)

---

## 📌 Problem Statement

Film and television productions operate under extreme daily financial risk. A major feature film burns **$85,000 to $250,000+ USD per day** in fixed overhead (cast, crew, equipment rentals, soundstages, location permits, logistics).

When unexpected real-world disruptions strike—an actor falling sick, a primary camera package failing, a location becoming unavailable, bad weather washing out outdoor filming, a Director of Photography missing call time, or an equipment transport van breaking down—line producers are forced to make high-stakes decisions under pressure.

**Production Chaos Controller** is an agentic AI system designed to autonomously detect disruption dependencies, evaluate schedule constraints, compute deterministic financial and calendar impacts, query high-throughput production telemetry via **ClickHouse**, and generate optimized, ranked recovery plans for producer sign-off.

---

## 🏗️ System Architecture

```
                               ┌──────────────────────────────────────────┐
                               │       Next.js 15 App Router Frontend     │
                               │  (Dark-Theme Production Control Center)  │
                               └────────────────────┬─────────────────────┘
                                                    │ REST API
                                                    ▼
                               ┌──────────────────────────────────────────┐
                               │           FastAPI Backend Engine         │
                               └──────────┬────────────────────┬──────────┘
                                          │                    │
                ┌─────────────────────────┴────────┐  ┌────────┴────────────────────────┐
                │ ProductionManagerAgent &         │  │ Official ClickHouse &          │
                │ Google Gemini 2.0 Flash SDK      │  │ MCP Tool Server Integration    │
                └─────────────────────────┬────────┘  └────────┬────────────────────────┘
                                          │                    │
                                          ▼                    ▼
                               ┌──────────────────────────────────────────┐
                               │   Deterministic Scheduling Engine        │
                               │ (Scenes, Cast, Equipment, Weather, Crew) │
                               └──────────────────────────────────────────┘
```

---

## ✨ Key Features & Disruption Scenarios

### 1. Primary Disruption Scenarios
- 🎭 **Actor Unavailability**: Resolves lead/supporting actor absence by finding indoor cover set swaps (0-day delay) or calculating calendar extensions ($85k/day penalty).
- 🎥 **Equipment Failure**: Identifies broken camera/grip packages, checks equipment compatibility, evaluates crew authorization, and dispatches emergency hot-courier rentals.
- 🏢 **Location Unavailability**: Detects location closures, evaluates alternative approved standing sets (e.g. Metro Medical Center Set), and checks actor/crew travel feasibility.
- 🌧️ **Bad Weather Forecast**: Identifies rain/blizzard sensitive outdoor scenes, shifts production to Stage 4 soundstage indoor cover sets, and defers outdoor filming to clear weather windows.
- 👥 **Crew Unavailability**: Resolves missing key crew (e.g., Director of Photography) by promoting internal qualified operators or hiring emergency day-players.
- 🚚 **Transportation & Logistics Breakdown**: Handles transit delays for equipment/crew vehicles, dispatches backup hot-shot couriers, and adjusts call times dynamically.

### 2. Multi-Disruption "Chaos Mode" Engine
- Analyzes multiple simultaneous disruptions (e.g., *Lead Actor Sick + Camera Failure + Heavy Rain on Day 6*).
- Builds a unified multi-entity dependency graph.
- Detects collisions between independent recovery plans (e.g. soundstage double-booking).
- Generates combined, collision-free master recovery plans.

### 3. ClickHouse Production Analytics & MCP Server
- Uses official `clickhouse-connect` SDK with 10 `MergeTree` tables (`scenes`, `shooting_schedules`, `actors`, `crew`, `equipment`, `locations`, `production_events`, `disruption_history`, `recovery_plans`, `cost_records`).
- Exposes 6 canonical analytics queries (actor dependencies, equipment utilization, high-risk resource ranking, disruption financial summary, lowest-cost movable scenes).
- Features an official **Model Context Protocol (MCP)** tool server (`/api/v1/mcp/clickhouse`).
- Operates with zero-downtime memory fallback when ClickHouse server is offline.

### 4. Human-in-the-Loop Sign-Off Controls
- Every AI recovery recommendation defaults to `requires_human_approval: true`.
- Line producers can **Approve**, **Reject**, or **Modify** proposed recovery plans directly from the UI.

---

## 🛠️ Tech Stack & Requirements

- **Backend**: Python 3.12+, FastAPI, Pydantic v2, `google-genai` SDK, `clickhouse-connect`, `uv`.
- **Frontend**: Next.js 15 (App Router), TypeScript, Tailwind CSS, Lucide Icons.
- **Database / Partner Integration**: ClickHouse (MergeTree tables) + Local In-Memory Fallback.
- **AI Intelligence**: Google Gemini 2.0 Flash + Google Cloud Agent Builder / ADK architecture.

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.12+
- `uv` installed (`pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh`)
- Node.js 18+ and `npm`

### 1. Environment Setup
Copy the environment template in the project root:

```bash
cp .env.example .env
cp backend/.env.example backend/.env
```

*(Optional)* Set your Google Gemini API key in `.env`:
```env
GEMINI_API_KEY="your-gemini-api-key-here"
```

### 2. Start Backend Server
```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```
- API Base URL: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/api/v1/health`

### 3. Start Frontend Development Server
Open a new terminal window:

```bash
cd frontend
npm install
npm run dev
```
- Dashboard URL: `http://localhost:3000`

---

## 🧪 Running Automated Tests

### Backend Pytest Suite
Run all 34 backend unit, integration, edge-case, and ClickHouse tests:

```bash
cd backend
uv run pytest
```

### Frontend TypeScript & Static Build Check
Verify zero TypeScript compilation errors:

```bash
cd frontend
npm run build
```

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | `""` | Optional Google Gemini API key for live AI reasoning synthesis |
| `GOOGLE_CLOUD_PROJECT` | `""` | Google Cloud Project ID for Agent Builder |
| `CLICKHOUSE_HOST` | `"localhost"` | ClickHouse database server hostname |
| `CLICKHOUSE_PORT` | `8123` | ClickHouse HTTP port |
| `CLICKHOUSE_USER` | `"default"` | ClickHouse username |
| `CLICKHOUSE_PASSWORD` | `""` | ClickHouse password |
| `CLICKHOUSE_DB` | `"production_chaos"` | ClickHouse database name |
| `NEXT_PUBLIC_API_BASE_URL` | `"http://localhost:8000"` | Next.js frontend backend API URI |

---

## 🎯 Hackathon Demo Flow (5-Minute Walkthrough)

1. **Dashboard Overview (`/`)**:
   - Show active film production *"The Last Signal"* (Current Day: Day 6 of 10, Burn Rate: $85,000/day).
   - Point out system status and active disruption counts.

2. **Simulate Equipment Failure (`/disruptions`)**:
   - Select **Equipment Failure** -> Resource: `RED V-Raptor 8K Camera Package` -> Day 5 -> Severity: Critical.
   - Click **Simulate Disruption**.
   - Watch animated agent steps: *Analyzing production... Finding dependencies... Checking resources... Generating recovery plans... Evaluating impact...*
   - Review 🚨 **IMPACT SUMMARY** (+ $3,500 USD, 0 Days Shift) and 🤖 **AI RECOMMENDATION** (Emergency Same-Day Rental Courier).

3. **Multi-Disruption "Chaos Mode" (`/disruptions`)**:
   - Click **Chaos Mode (Multi-Disruption)**.
   - Trigger simultaneous disruptions: *Lead Actor Sick + Camera Failure + Heavy Rain on Day 6*.
   - View combined dependency graph and collision avoidance rationale.

4. **ClickHouse Analytics & MCP Explorer (`/analytics`)**:
   - View live ClickHouse status indicator (`active` or `fallback`).
   - Run the 6 canonical production queries (e.g. *Scenes by Actor*, *High-Risk Resource Ranking*, *Lowest-Impact Movable Scenes*).
   - Inspect official MCP tool manifest JSON (`/api/v1/mcp/clickhouse`).

5. **Producer Sign-off (`/recovery`)**:
   - Review candidate recovery options and click **Approve Plan** to execute the recovery workflow.
