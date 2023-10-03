.PHONY: init init-migration build run db-migrate test tox

init:  build run
	docker-compose exec web flask db init
	docker-compose exec web flask db migrate
	docker-compose exec web flask db upgrade
	docker-compose exec web flask init
	@echo "Init done, containers running"

build:
	docker-compose build

run:
	docker-compose up -d

db-init:
	docker-compose exec web flask db init

db-migrate:
	docker-compose exec web flask db migrate

db-upgrade:
	docker-compose exec web flask db upgrade

open-redis:
	docker exec -it filmapi_redis_1 redis-cli

test:
	docker-compose stop celery # stop celery to avoid conflicts with celery tests
	docker-compose start rabbitmq redis # ensuring both redis and rabbitmq are started
	docker-compose run --rm -v $(PWD)/tests:/code/tests:ro web tox -e test -- -v
	docker-compose start celery

tox:
	docker-compose stop celery # stop celery to avoid conflicts with celery tests
	docker-compose start rabbitmq redis # ensuring both redis and rabbitmq are started
	docker-compose run --rm -v $(PWD)/tests:/code/tests:ro web tox -e py311
	docker-compose start celery

lint:
	docker-compose run --rm web tox -e lint

clean:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf
