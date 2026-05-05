FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy bot package as a subdirectory so `python -m bot` resolves correctly.
COPY . ./bot/

EXPOSE 8080

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "bot"]
