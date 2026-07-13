FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install fastapi uvicorn pydantic requests websockets matplotlib networkx psycopg2-binary paho-mqtt
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--ws", "websockets"]