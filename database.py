import psycopg2
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Copy .env.example to .env, fill in real "
        "values, and run via `docker compose up` (which loads .env) or "
        "export DATABASE_URL yourself for local runs."
    )

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")

    # Note: no SERIAL/PRIMARY KEY on id alone — TimescaleDB hypertables
    # require the partitioning column (timestamp) in any uniqueness
    # constraint, so we key on (id, timestamp) instead.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id SERIAL,
            sensor_id VARCHAR(100),
            value FLOAT,
            timestamp TIMESTAMP NOT NULL,
            alert VARCHAR(255),
            PRIMARY KEY (id, timestamp)
        )
    """)

    # Convert to a hypertable (chunked by time) for efficient high-frequency
    # sensor writes and time-range queries. Safe to call repeatedly.
    cursor.execute("""
        SELECT create_hypertable('sensor_readings', 'timestamp',
                                  if_not_exists => TRUE)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sensor_readings_sensor_time
        ON sensor_readings (sensor_id, timestamp DESC)
    """)

    conn.commit()
    cursor.close()
    conn.close()

def save_reading(sensor_id, value, timestamp, alert=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sensor_readings (sensor_id, value, timestamp, alert)
        VALUES (%s, %s, %s, %s)
    """, (sensor_id, value, timestamp, alert))
    conn.commit()
    cursor.close()
    conn.close()

def get_recent_readings(limit=50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sensor_id, value, timestamp, alert 
        FROM sensor_readings 
        ORDER BY timestamp DESC 
        LIMIT %s
    """, (limit,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {"sensor_id": r[0], "value": r[1], 
         "timestamp": str(r[2]), "alert": r[3]} 
        for r in rows
    ]