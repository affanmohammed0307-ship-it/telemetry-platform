from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
import json, random

app = FastAPI()
data_store = []
active_connections = []

class SensorData(BaseModel):
    sensor_id: str
    value: float
    timestamp: str

@app.post("/ingest")
async def ingest(data: SensorData):
    record = data.dict()
    data_store.append(record)
    for ws in active_connections:
        await ws.send_text(json.dumps(record))
    return {"status": "ok"}

@app.get("/data")
def get_data():
    return data_store[-50:]

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
    <html>
    <body style="background:#111;color:#00ff88;font-family:monospace;padding:20px">
    <h2>🚗 Live Vehicle Telemetry</h2>
    <div id="stats" style="margin-bottom:16px;color:#888"></div>
    <div id="feed" style="font-size:13px;line-height:1.8"></div>
    <script>
      let count = 0;
      const ws = new WebSocket("ws://localhost:8000/ws");
      ws.onmessage = e => {
        const d = JSON.parse(e.data);
        count++;
        document.getElementById('stats').textContent = `${count} readings received`;
        const div = document.createElement('div');
        div.textContent = `[${d.timestamp}]  ${d.sensor_id}: ${d.value}`;
        document.getElementById('feed').prepend(div);
        if (document.getElementById('feed').children.length > 30) {
          document.getElementById('feed').lastChild.remove();
        }
      };
    </script>
    </body></html>
    """)