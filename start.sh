#!/usr/bin/env bash
set -euo pipefail

# Get PORT from environment, default to 8000
PORT_NUM="${PORT:-8000}"

echo "=========================================="
echo "SONA System Starting"
echo "Port: ${PORT_NUM}"
echo "=========================================="

# Run migrations
echo "Running database migrations..."
python manage.py migrate --no-input

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Create demo data if tables are empty
echo "Loading demo data..."
python manage.py create_demo_data || echo "Demo data already exists or failed to load"

echo "=========================================="
echo "Starting web server..."
echo "=========================================="

# Start Gunicorn with the actual port number
exec python -m gunicorn config.wsgi:application --bind 0.0.0.0:"${PORT_NUM}" --workers 2 --timeout 120

