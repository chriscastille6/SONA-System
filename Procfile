web: python -m gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}
release: python manage.py migrate --no-input && python manage.py collectstatic --no-input && python manage.py create_demo_data

