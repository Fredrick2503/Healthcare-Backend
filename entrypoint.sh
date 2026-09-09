#!/bin/sh

set -e

# Wait for PostgreSQL if configured and SQLite is not explicitly enabled
if [ -n "$DB_HOST" ] && [ "$USE_SQLITE" != "True" ] && [ "$USE_SQLITE" != "true" ] && [ "$USE_SQLITE" != "1" ]; then
    echo "==> Checking PostgreSQL readiness at $DB_HOST:${DB_PORT:-5432}..."
    while ! nc -z "$DB_HOST" "${DB_PORT:-5432}"; do
        echo "Waiting for PostgreSQL at $DB_HOST:${DB_PORT:-5432}..."
        sleep 1
    done
    echo "==> PostgreSQL is ready!"
fi

# Wait for Redis if configured and enabled
if [ -n "$REDIS_URL" ] && [ "$USE_REDIS_FOR_JWT" != "False" ] && [ "$USE_REDIS_FOR_JWT" != "false" ] && [ "$USE_REDIS_FOR_JWT" != "0" ]; then
    REDIS_HOST=$(echo "$REDIS_URL" | sed -e 's,^redis://,,' -e 's,:[0-9]*/.*$,,' -e 's,/.*$,,')
    REDIS_PORT=6379
    echo "==> Checking Redis readiness at $REDIS_HOST:$REDIS_PORT..."
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
