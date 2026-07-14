#!/bin/sh
# Container start: apply migrations, gather static files, then run gunicorn.
# Static/media are served by the sidecar nginx from shared volumes.
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn campanarium.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120
