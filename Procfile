web: gunicorn magnet.wsgi --log-file -
worker: celery worker --app=tasks.app
