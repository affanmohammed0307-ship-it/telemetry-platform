# Real-Time Telemetry Platform

Live multi-sensor data ingestion and streaming built with FastAPI, WebSockets, and Python.

## What it does
- Ingests high-frequency sensor data via REST API
- Streams live data to connected clients in real time via WebSocket
- Supports multiple simultaneous sensors (engine temp, battery voltage, etc.)
- Stores last 50 readings accessible via REST endpoint

## Quick start
pip install fastapi uvicorn pydantic requests websockets
python -m uvicorn main:app --reload --ws websockets

## How it works
Sensor → POST /ingest → FastAPI → WebSocket broadcast → Live dashboard
                                ↓
                          data_store (last 50 readings)

## API
- POST /ingest — send sensor reading
- GET /data — retrieve last 50 readings
- GET / — live streaming dashboard
- WS /ws — WebSocket connection for real-time updates

## Why I built this
Vehicle telemetry, industrial IoT, and robotics systems all share the same 

## Knowledge Graph
Built a vehicle sensor knowledge graph using NetworkX representing 
relationships between sensors, systems and the telemetry platform.

![Knowledge Graph](knowledge_graph.png)
core problem: high-frequency data that needs to be ingested, processed, and 
visualized in real time. This is my working implementation of that pipeline.

## Stack
FastAPI · WebSockets · Python 3.11
