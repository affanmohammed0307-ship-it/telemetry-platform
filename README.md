# 🚗 Vehicle Health Monitor

Real-time vehicle sensor monitoring with intelligent anomaly detection, live dashboards, an MQTT event broker, TimescaleDB persistence, Grafana metrics, and Docker deployment.

![Dashboard]<img width="1913" height="1086" alt="dashboard" src="https://github.com/user-attachments/assets/11f276e6-fe46-4e55-b2a7-83ba0315c938" />


## What it does

- Simulates a fleet of vehicle sensors publishing over MQTT (Mosquitto), decoupled from the backend like a real IoT deployment
- Streams data to all connected clients instantly via WebSocket
- Detects anomalies in real time with intelligent diagnosis — critical alerts, warnings, and info messages with root cause explanations
- Persists all readings and alerts in TimescaleDB (a time-series-optimized Postgres) — data survives restarts and scales to high-frequency logging
- Live Chart.js charts updating every 500ms, plus a provisioned Grafana dashboard for historical metrics and alert counts
- Full Docker Compose deployment — one command spins everything up

## Quick Start

```bash
docker compose up --build
```

- Live dashboard: http://localhost:8000
- Grafana: http://localhost:3000 (anonymous viewer access enabled; admin/admin for editing)

## Architecture

```
Sensor Simulator → MQTT Broker (Mosquitto) → FastAPI subscriber → Anomaly Detection → Alert Generated
   (fleet of N)      (vehicle/sensors/#)            ↓                                    ↓
                                              TimescaleDB                        WebSocket Broadcast
                                           (hypertable, persist all)                     ↓
                                                    ↓                            Live Dashboard
                                                Grafana                          (Chart.js + Alerts)
                                        (historical charts, alert stats)
```

`POST /ingest` still exists as a manual/debug entry point into the same pipeline, but normal operation flows entirely through MQTT.

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
| `/ingest` | POST | Manual/debug sensor reading (normal flow is via MQTT) |
| `/data` | GET | Retrieve last 50 readings with alerts |
| `/` | GET | Live dashboard |
| `/ws` | WebSocket | Real-time updates |

MQTT topic: sensors publish JSON `{sensor_id, value, timestamp}` to `vehicle/sensors/<sensor_id>` on the broker (`mqtt:1883` in Docker, `localhost:1883` locally).

## Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Python 3.11 |
| Event Broker | MQTT (Eclipse Mosquitto) |
| Real-time | WebSockets |
| Database | TimescaleDB (PostgreSQL 15 + hypertables) |
| Metrics | Grafana |
| Frontend | Chart.js |
| Deployment | Docker Compose |
| Graph | NetworkX |

## Project Structure

```
telemetry/
├── main.py                          # FastAPI app, MQTT subscriber wiring, WebSocket, dashboard
├── mqtt_client.py                   # MQTT bridge: subscribes and feeds the ingest pipeline
├── database.py                      # TimescaleDB connection, hypertable setup, queries
├── alerts.py                        # Anomaly detection and diagnosis logic
├── simulate.py                      # Multi-sensor data simulator (publishes over MQTT)
├── knowledge_graph.py               # Vehicle sensor relationship graph
├── mosquitto/config/                # MQTT broker config
├── grafana/provisioning/            # Grafana datasource + dashboard provisioning
├── Dockerfile                       # Container definition
├── docker-compose.yml               # Full stack orchestration (app, mqtt, db, grafana, simulator)
├── dashboard.png                    # Live dashboard screenshot
└── knowledge_graph.png              # Sensor knowledge graph
```

## Why I built this

Vehicle telemetry, industrial IoT, and robotics systems all share the same core problem: high-frequency sensor data that needs to be ingested, processed, and acted on in real time. This project implements a complete production-ready pipeline — from raw sensor input to intelligent diagnosis — containerized and deployable in one command.
