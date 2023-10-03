FLASK_ENV=development
FLASK_APP=filmapi.app:create_app
SECRET_KEY=changeme
DATABASE_URI=postgresql://admin:admin@postgres:5432/filmapi

CELERY_BROKER_URL=amqp://guest:guest@rabbitmq
CELERY_RESULT_BACKEND_URL=redis://redis
