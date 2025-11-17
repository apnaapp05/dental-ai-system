# --- STAGE 1: BUILDER ---
FROM python:3.11-slim AS builder
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# install build deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc \
 && rm -rf /var/lib/apt/lists/*

# copy requirements and build wheels
COPY requirements.txt /app/requirements.txt
RUN pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r /app/requirements.txt

# --- STAGE 2: RUNTIME ---
FROM python:3.11-slim AS runtime
ENV PYTHONUNBUFFERED=1
ENV AGENT_NAME=AppointmentAgent
WORKDIR /app

# copy wheels and requirements from builder and install them
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /app/requirements.txt /app/requirements.txt
RUN pip install --no-index --find-links /wheels -r /app/requirements.txt

# copy application code
COPY . /app

# expose port (informational only)
EXPOSE 8080

# run the server
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "agent_server:app", "--bind", "0.0.0.0:8080"]
