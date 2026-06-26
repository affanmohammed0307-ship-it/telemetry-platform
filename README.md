# 🚗 Vehicle Health Monitor

Real-time vehicle sensor monitoring with intelligent anomaly detection, live dashboards, PostgreSQL persistence, and Docker deployment.

![Dashboard](<img width="1913" height="1086" alt="dashboard" src="https://github.com/user-attachments/assets/8bf19dbd-a2ee-47e4-b781-6ca00aa8605c" />
)

## What it does

- Ingests live multi-sensor vehicle data via REST API
- Streams data to all connected clients instantly via WebSocket
- Detects anomalies in real time with intelligent diagnosis — critical alerts, warnings, and info messages with root cause explanations
- Persists all readings and alerts in PostgreSQL — data survives restarts
- Live Chart.js charts updating every 500ms
- Full Docker Compose deployment — one command spins everything up

## Quick Start

```bash
docker compose up --build
```

Open http://localhost:8000

## Architecture

```
Sensor → POST /ingest → FastAPI → Anomaly Detection → Alert Generated
                               ↓                    ↓
                         PostgreSQL          WebSocket Broadcast
                         (persist all)             ↓
                                          Live Dashboard
                                          (Chart.js + Alerts)
```

## Knowledge Graph

Models semantic relationships between vehicle sensors and systems.

![Knowledge Graph](knowledge_graph.png)

## Alert Logic

| Sensor | Condition | Severity | Diagnosis |
|---|---|---|---|
| engine_temp | > 115°C | 🔴 CRITICAL | Coolant leak, thermostat failure, blocked radiator |
| engine_temp | > 105°C | 🟠 WARNING | Cooling system stress — monitor closely |
| engine_temp | < 85°C | 🔵 INFO | Thermostat stuck open, short trip cycle |
| battery_voltage | < 11.8V | 🔴 CRITICAL | Alternator failure, parasitic drain, aging battery |
| battery_voltage | < 12.2V | 🟠 WARNING | Below optimal — check charging system |
| battery_voltage | > 14.8V | 🔴 CRITICAL | Overcharging — faulty voltage regulator |

## API

| Endpoint | Method | Description |
|---|---|---|
| `/ingest` | POST | Send sensor reading |
| `/data` | GET | Retrieve last 50 readings with alerts |
| `/` | GET | Live dashboard |
| `/ws` | WebSocket | Real-time updates |

## Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Python 3.11 |
| Real-time | WebSockets |
| Database | PostgreSQL 15 |
| Frontend | Chart.js |
| Deployment | Docker Compose |
| Graph | NetworkX |

## Project Structure

```
telemetry/
├── main.py              # FastAPI app, WebSocket, dashboard
├── database.py          # PostgreSQL connection and queries
├── alerts.py            # Anomaly detection and diagnosis logic
├── simulate.py          # Multi-sensor data simulator
├── knowledge_graph.py   # Vehicle sensor relationship graph
├── Dockerfile           # Container definition
├── docker-compose.yml   # Full stack orchestration
├── dashboard.png        # Live dashboard screenshot
└── knowledge_graph.png  # Sensor knowledge graph
```

## Why I built this

Vehicle telemetry, industrial IoT, and robotics systems all share the same core problem: high-frequency sensor data that needs to be ingested, processed, and acted on in real time. This project implements a complete production-ready pipeline — from raw sensor input to intelligent diagnosis — containerized and deployable in one command.
