#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
echo "Starting Django server on http://127.0.0.1:8000/"
echo "Press Ctrl+C to stop"
python manage.py runserver 127.0.0.1:8000


