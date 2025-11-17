# --- STAGE 1: BUILDER ---
FROM python:3.11-slim AS builder
ENV PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /app/
RUN pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements.txt

# --- STAGE 2: RUNTIME ---
FROM python:3.11-slim AS runtime
ENV PYTHONUNBUFFERED=1
ENV AGENT_NAME=AppointmentAgent
WORKDIR /app
COPY --from=builder /usr/src/app/wheels /usr/src/app/wheels
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . /app

# The command executes the agent API service with concurrency for high availability.
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "agent_server:app", "--bind", "0.0.0.0:8080"]
