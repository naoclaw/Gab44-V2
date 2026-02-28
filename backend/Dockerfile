FROM python:3.11-slim

# Install C build tools required by pyswisseph and other native extensions.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (layer cache-friendly).
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy application source.
COPY . .

# Expose the port the app listens on.
EXPOSE 8001

# Use gunicorn + uvicorn workers for multi-core throughput.
# ECS Fargate task CPU/memory determines the effective worker count.
# Adjust --workers to match (vCPU × 2 + 1) for your task size.
CMD ["gunicorn", "server:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "2", \
     "--bind", "0.0.0.0:8001", \
     "--timeout", "120", \
     "--keep-alive", "5", \
     "--log-level", "info"]
