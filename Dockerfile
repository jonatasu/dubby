# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies for audio processing and translation
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    espeak \
    espeak-data \
    pulseaudio \
    alsa-utils \
    libsndfile1 \
    git \
    curl \
    wget \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p models uploads outputs logs

# Download ASR model during build
RUN python scripts/download_whisper_model.py

# Initialize translation service
RUN python -c "from app.services.translate import initialize_translation_service; initialize_translation_service()" || echo "Translation initialization will be done at runtime"

EXPOSE 8000

ENV PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
