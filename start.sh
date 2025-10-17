#!/usr/bin/env bash
set -euo pipefail

# Get PORT from environment, default to 8000
PORT_NUM="${PORT:-8000}"

echo "=========================================="
echo "SONA System Starting"
echo "Port: ${PORT_NUM}"
echo "=========================================="

# Start Gunicorn with the actual port number
exec python -m gunicorn config.wsgi:application --bind 0.0.0.0:"${PORT_NUM}" --workers 2 --timeout 120

