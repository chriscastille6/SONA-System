web: gunicorn config.wsgi --bind 0.0.0.0:$PORT
release: python manage.py migrate --no-input && python manage.py collectstatic --no-input && python manage.py create_demo_data

