"""Default configuration

Use env var to override
"""
import os

ENV = os.getenv("FLASK_ENV")
DEBUG = ENV == "development"
SECRET_KEY = os.getenv("SECRET_KEY")

CACHE_TYPE = "RedisCache"
CACHE_DEFAULT_TIMEOUT = 30
CACHE_REDIS_HOST = "redis"

SQLALCHEMY_RECORD_QUERIES = True
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
SQLALCHEMY_TRACK_MODIFICATIONS = False

ELASTICSEARCH_CONFIG = {
    "hosts": os.getenv("ELASTICSEARCH"),
    "http_auth": (os.getenv("ES_USER"), os.getenv("ES_PASS")),
}

CELERY = {
    "broker_url": os.getenv("CELERY_BROKER_URL"),
    "result_backend": os.getenv("CELERY_RESULT_BACKEND_URL"),
    "broker_connection_retry_on_startup": True,
}

HEADERS = {
    "authority": "www.imdb.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,\
               */*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7,uk;q=0.6,de;q=0.5",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
                   Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.43",
}
