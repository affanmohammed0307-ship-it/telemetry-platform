import requests
import time
import random
from datetime import datetime

while True:
    requests.post('http://localhost:8000/ingest', json={
        'sensor_id': 'engine_temp',
        'value': round(random.uniform(80, 120), 2),
        'timestamp': datetime.utcnow().isoformat()
    })
    requests.post('http://localhost:8000/ingest', json={
        'sensor_id': 'battery_voltage',
        'value': round(random.uniform(11.5, 14.5), 2),
        'timestamp': datetime.utcnow().isoformat()
    })
    time.sleep(0.5)