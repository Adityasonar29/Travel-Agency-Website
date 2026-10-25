#!/bin/sh

python manage.py run_email_worker &
worker_pid=$!

gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-8000}" &
web_pid=$!

shutdown() {
    kill -TERM "$worker_pid" "$web_pid" 2>/dev/null || true
    wait "$worker_pid" 2>/dev/null || true
    wait "$web_pid" 2>/dev/null || true
}

trap shutdown INT TERM

wait "$web_pid"
web_status=$?
shutdown
trap - INT TERM
exit "$web_status"
