FROM python:3.11-slim

# ffmpeg pour l'extraction audio
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY templates/ ./templates/

RUN mkdir -p /data/media

ENV FLASK_DEBUG=0 \
    DB_PATH=/data/podcast.db \
    MEDIA_DIR=/data/media

EXPOSE 5000

CMD ["gunicorn", "--workers=2", "--bind=0.0.0.0:5000", "--timeout=120", "--chdir=/app/src", "wsgi:app"]
