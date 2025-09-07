web: gunicorn airbnb_clone.wsgi:application --log-file -
worker: celery -A airbnb_clone worker --loglevel=info
beat: celery -A airbnb_clone beat --loglevel=info