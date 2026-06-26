import psycopg2
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://affan:telemetry123@localhost:5432/telemetry")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id SERIAL PRIMARY KEY,
            sensor_id VARCHAR(100),
            value FLOAT,
            timestamp TIMESTAMP,
            alert VARCHAR(255)
        )
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