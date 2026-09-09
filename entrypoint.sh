#!/bin/sh

set -e

echo "==> Checking PostgreSQL readiness..."
if [ -n "$DB_HOST" ]; then
    while ! nc -z "$DB_HOST" "${DB_PORT:-5432}"; do
        echo "Waiting for PostgreSQL at $DB_HOST:${DB_PORT:-5432}..."
        sleep 1
    done
    echo "==> PostgreSQL is ready!"
fi

echo "==> Checking Redis readiness..."
if [ -n "$REDIS_URL" ]; then
    REDIS_HOST=$(echo "$REDIS_URL" | sed -e 's,^redis://,,' -e 's,:[0-9]*/.*$,,' -e 's,/.*$,,')
    REDIS_PORT=6379
    while ! nc -z "$REDIS_HOST" "$REDIS_PORT"; do
        echo "Waiting for Redis at $REDIS_HOST:$REDIS_PORT..."
        sleep 1
    done
    echo "==> Redis is ready!"
fi

echo "==> Applying database migrations..."
python manage.py migrate --no-input

echo "==> Starting application..."
exec "$@"
