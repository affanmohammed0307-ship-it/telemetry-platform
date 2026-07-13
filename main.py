from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
import json, random
from alerts import check_alert
from database import init_db, save_reading, get_recent_readings
from mqtt_client import MQTTBridge

app = FastAPI()
active_connections = []
mqtt_bridge = None


async def handle_reading(sensor_id: str, value: float, timestamp: str):
    """Shared pipeline: anomaly check -> persist -> broadcast. Used by both
    the MQTT bridge and the /ingest REST endpoint."""
    alert = check_alert(sensor_id, value)
    save_reading(sensor_id, value, timestamp, alert)
    record = {"sensor_id": sensor_id, "value": value, "timestamp": timestamp, "alert": alert}
    for ws in list(active_connections):
        try:
            await ws.send_text(json.dumps(record))
        except Exception:
            pass
    return alert


@app.on_event("startup")
def startup():
    global mqtt_bridge
    init_db()
    mqtt_bridge = MQTTBridge(handle_reading)
    mqtt_bridge.start()


@app.on_event("shutdown")
def shutdown():
    if mqtt_bridge:
        mqtt_bridge.stop()

class SensorData(BaseModel):
    sensor_id: str
    value: float
    timestamp: str

@app.post("/ingest")
async def ingest(data: SensorData):
    """Manual/debug ingestion path. In normal operation, sensors publish to
    MQTT (see mqtt_client.py) and this pipeline runs via the bridge instead."""
    alert = await handle_reading(data.sensor_id, data.value, data.timestamp)
    return {"status": "ok", "alert": alert}

@app.get("/data")
def get_data():
    return get_recent_readings()

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    active_connections.append(ws)
    try:
        while True:
            await ws.receive_text()
    except:
        active_connections.remove(ws)

@app.get("/")
def dashboard():
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>Vehicle Telemetry</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { background:#0d0d0d; color:#fff; font-family:monospace; padding:20px; }
        h2 { color:#00ff88; }
        .grid { display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-top:20px; }
        .card { background:#1a1a1a; border-radius:10px; padding:15px; }
        .alert-box { margin-top:20px; background:#1a1a1a; border-radius:10px; padding:15px; min-height:60px; }
        .alert-box p { margin:5px 0; font-size:13px; }
        .stat { font-size:28px; font-weight:bold; color:#00ff88; }
        .label { font-size:12px; color:#888; margin-bottom:8px; }
    </style>
</head>
<body>
    <h2>🚗 Vehicle Health Monitor</h2>

    <div class="grid">
        <div class="card">
            <div class="label">ENGINE TEMPERATURE</div>
            <div class="stat" id="temp_val">--</div>
            <canvas id="tempChart" height="100"></canvas>
        </div>
        <div class="card">
            <div class="label">BATTERY VOLTAGE</div>
            <div class="stat" id="batt_val">--</div>
            <canvas id="battChart" height="100"></canvas>
        </div>
    </div>

    <div class="alert-box">
        <div class="label">⚡ LIVE ALERTS</div>
        <div id="alerts"></div>
    </div>

    <script>
        const tempData = { labels: [], datasets: [{ label: 'Engine Temp (°C)', data: [], borderColor: '#ff4444', tension: 0.3, fill: false }] };
        const battData = { labels: [], datasets: [{ label: 'Battery Voltage (V)', data: [], borderColor: '#00ff88', tension: 0.3, fill: false }] };

        const tempChart = new Chart(document.getElementById('tempChart'), { type: 'line', data: tempData, options: { animation: false, plugins: { legend: { labels: { color: '#fff' } } }, scales: { x: { ticks: { color: '#888' }, display: false }, y: { ticks: { color: '#888' } } } } });
        const battChart = new Chart(document.getElementById('battChart'), { type: 'line', data: battData, options: { animation: false, plugins: { legend: { labels: { color: '#fff' } } }, scales: { x: { ticks: { color: '#888' }, display: false }, y: { ticks: { color: '#888' } } } } });

        const ws = new WebSocket("ws://localhost:8000/ws");
        ws.onmessage = e => {
            const d = JSON.parse(e.data);
            const time = new Date(d.timestamp).toLocaleTimeString();

            if (d.sensor_id === 'engine_temp') {
                document.getElementById('temp_val').textContent = d.value + ' °C';
                tempData.labels.push(time);
                tempData.datasets[0].data.push(d.value);
                if (tempData.labels.length > 30) { tempData.labels.shift(); tempData.datasets[0].data.shift(); }
                tempChart.update();
            }

            if (d.sensor_id === 'battery_voltage') {
                document.getElementById('batt_val').textContent = d.value + ' V';
                battData.labels.push(time);
                battData.datasets[0].data.push(d.value);
                if (battData.labels.length > 30) { battData.labels.shift(); battData.datasets[0].data.shift(); }
                battChart.update();
            }

            if (d.alert) {
                const alertDiv = document.getElementById('alerts');
                const p = document.createElement('p');
                p.textContent = '[' + time + '] ' + d.alert;
                p.style.color = d.alert.includes('CRITICAL') ? '#ff4444' : d.alert.includes('WARNING') ? '#ffaa00' : '#00aaff';
                alertDiv.prepend(p);
                if (alertDiv.children.length > 5) alertDiv.lastChild.remove();
            }
        };
    </script>
</body>
</html>
    """)