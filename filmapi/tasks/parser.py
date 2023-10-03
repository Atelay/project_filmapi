import asyncio
from filmapi.extensions import celery, db
from filmapi.services.film_service import FilmService
from filmapi.services.imdb_parser import IMDbParser
from flask import current_app as app


@celery.task
def parse_imdb_data(link=None):
    headers = app.config.get("HEADERS", {})
    scraper = IMDbParser(headers)

    if link:
        films = asyncio.run(scraper.parse_movies(link))
        FilmService.bulk_create_films(db.session, films)
        return f"{films[0].title} added to database"
    else:
        films = asyncio.run(scraper.parse_movies())
        FilmService.bulk_create_films(db.session, films)
        return f"{len(films)} films added to database"
