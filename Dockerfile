# Container image for the klokkenInventaris Django app (GeoDjango + gunicorn).
# Build context is this repo root; the Django project lives in campanarium/.
FROM python:3.12-slim

# GeoDjango loads GDAL/GEOS/PROJ at runtime via ctypes. psycopg2-binary bundles
# libpq, so no libpq-dev is needed. gettext is not used (no translations).
RUN apt-get update && apt-get install -y --no-install-recommends \
        binutils \
        libproj-dev \
        gdal-bin \
        libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project (manage.py + campanarium/ + inventory/) to /app,
# and the entrypoint (which lives at the repo root, next to this Dockerfile).
COPY campanarium/ .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
