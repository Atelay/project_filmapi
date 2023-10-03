# FilmAPI

![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

FilmAPI is a project created for the purpose of self-learning, providing a RESTful API that can serve as part of the backend for a movie website. It features a data parser for movies from the IMDb website based on the provided link. Thanks to Celery, it allows for concurrent parsing of multiple movies, monitoring progress using the Flower service.

## Features

- Implementation of movie filtering based on various criteria such as genre, release year, and rating, along with pagination.
- Result caching using Redis to reduce database load.
- Convenient addition of movies to the database with simultaneous indexing in Elasticsearch.
- Implementation of a movie search resource in the database using the Elasticsearch service.
- Makefile with multiple commands for easy project management.
- Swagger documentation for resource testing.
- Configured Dockerfile allowing you to set up the project with a single command, despite the multitude of different services.

## Installation

To run the project, you will need [Docker](https://www.docker.com/) installed. Follow these steps to install and run the project:

1. Clone the repository.

2. Create a `.flaskenv` file and set the necessary environment variables:

```
FLASK_ENV=development
FLASK_APP=filmapi.app:create_app
SECRET_KEY=changeme
DATABASE_URI=postgresql://admin:admin@postgres:5432/filmapi

CELERY_BROKER_URL=amqp://guest:guest@rabbitmq
CELERY_RESULT_BACKEND_URL=redis://redis
```
2. Create a `.testenv` file for testing:

```
SECRET_KEY=testing
DATABASE_URI=sqlite:///:memory:
CELERY_BROKER_URL=amqp://guest:guest@localhost/
CELERY_RESULT_BACKEND_URL=amqp://guest:guest@localhost/
```
3. Initialize and start the containers:

```
make init
```

After successfully executing this command, you should have `8 Docker containers` up and running.

## Containers

- `web` - The Flask application container.
- `postgres` - The PostgreSQL database container.
- `pgadmin` - The pgAdmin database management tool container.
- `rabbitmq` - The RabbitMQ message broker container.
- `redis` - The Redis cache container.
- `celery` - The Celery task worker container.
- `flower` - The Flower Celery task monitoring tool container.
- `elasticsearch` - The Elasticsearch search engine container.


## Monitoring
- The application with the Swagger documentation will be available at:
```
http://localhost:5000/swagger-ui
```

- You can access pgAdmin at the following URL: 
```
http://localhost:5050
```
- You can access Flower for monitoring Celery tasks at the following URL:
```
http://localhost:5555
```

## Makefile Commands

- `init`: Project initialization, building, creating the admin user and container startup.
- `test`: Run project tests.
- `lint`: Run the linter to check the code.
- `tox`: Code linting with subsequent testing.
- `clean`: Clean Python-related files.

