"""
MQTT bridge: subscribes to the sensor topic on the broker and feeds every
message into the same pipeline the /ingest REST endpoint uses (anomaly
detection -> persistence -> websocket broadcast).

This mimics a real IoT fleet: sensors publish to MQTT instead of calling
the API directly, and the broker decouples producers from the backend.
"""
import asyncio
import json
import os
import paho.mqtt.client as mqtt

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "vehicle/sensors/#")


class MQTTBridge:
    def __init__(self, on_message_coro):
        """
        on_message_coro: async function(sensor_id, value, timestamp) called
        for every message received, scheduled onto the FastAPI event loop.
        """
        self.on_message_coro = on_message_coro
        self.loop = None
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="telemetry-backend")
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        client.subscribe(MQTT_TOPIC)

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            sensor_id = payload["sensor_id"]
            value = payload["value"]
            timestamp = payload["timestamp"]
        except (KeyError, json.JSONDecodeError, UnicodeDecodeError):
            return

        if self.loop is not None:
            asyncio.run_coroutine_threadsafe(
                self.on_message_coro(sensor_id, value, timestamp), self.loop
            )

    def start(self):
        self.loop = asyncio.get_event_loop()
        self.client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
