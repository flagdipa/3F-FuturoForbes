# Production Dockerfile for FuturoForbes
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir uvicorn

# Copy application code
COPY . .

# Environment defaults
ENV PORT=8000
ENV HOST=0.0.0.0

EXPOSE 8000

# Run with uvicorn
CMD ["sh", "-c", "python -m uvicorn backend.main:app --host $HOST --port $PORT"]
