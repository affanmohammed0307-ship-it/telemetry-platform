"""
Simulates a fleet of vehicle sensors publishing readings onto the MQTT
broker, the way real IoT devices would — decoupled from the backend, with
the broker handling fan-out/buffering instead of direct HTTP calls.
"""
import json
import os
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="sensor-simulator")
client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
client.loop_start()


def publish(sensor_id, value):
    payload = {
        "sensor_id": sensor_id,
        "value": value,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    client.publish(f"vehicle/sensors/{sensor_id}", json.dumps(payload))


if __name__ == "__main__":
    try:
        while True:
            publish("engine_temp", round(random.uniform(80, 120), 2))
            publish("battery_voltage", round(random.uniform(11.5, 14.5), 2))
            time.sleep(0.5)
    except KeyboardInterrupt:
        client.loop_stop()
        client.disconnect()
