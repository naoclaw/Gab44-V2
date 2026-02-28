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

# Start the ASGI server.
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
