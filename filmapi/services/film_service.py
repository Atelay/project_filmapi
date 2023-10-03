from datetime import date
from sqlalchemy import func
from filmapi.models import Actor, Film, Genre, MoviesGenres
from sqlalchemy.orm.session import Session
from filmapi.api.schemas import FilmSchema


class FilmService:
    @staticmethod
    def fetch_all_films(
        session: Session, page, offset, year_from=None, year_to=None, rating_from=None
    ):
        query = (
            session.query(
                Film.title,
                Film.uuid,
                Film.title_original,
                Film.poster,
                Film.rating,
                Film.description,
                Film.release_date,
            )
            .join(MoviesGenres, MoviesGenres.film_id == Film.id)
            .group_by(Film.id)
        )

        if year_from:
            query = query.filter(Film.release_date >= date(year_from, 1, 1))
        if year_to:
            query = query.filter(Film.release_date <= date(year_to, 12, 31))
        if rating_from:
            query = query.filter(Film.rating >= rating_from)
        return query.offset(page * offset).limit(offset)

    @classmethod
    def fetch_film_by_uuid(cls, session: Session, uuid):
        return session.query(Film).filter_by(uuid=uuid)

    @staticmethod
    def fetch_films_by_genre(
        session: Session,
        genre_name,
        page,
        offset,
        year_from=None,
        year_to=None,
        rating_from=None,
    ):
        query = (
            session.query(
                Film.title,
                Film.uuid,
                Film.title_original,
                Film.poster,
                Film.rating,
                Film.description,
                Film.release_date,
            )
            .join(MoviesGenres, MoviesGenres.film_id == Film.id)
            .join(Genre, Genre.id == MoviesGenres.genre_id)
            .group_by(Film.id)
            .filter(func.lower(Genre.name) == genre_name.lower())
        )
        if year_from:
            query = query.filter(Film.release_date >= date(year_from, 1, 1))
        if year_to:
            query = query.filter(Film.release_date <= date(year_to, 12, 31))
        if rating_from:
            query = query.filter(Film.rating >= rating_from)
        return query.offset(page * offset).limit(offset)

    @staticmethod
    def bulk_create_films(session: Session, films):
        film_schema = FilmSchema()
        films_to_create = []

        all_actors = {actor.name: actor for actor in session.query(Actor).all()}
        all_genres = {genre.name: genre for genre in session.query(Genre).all()}

        for film_data in films:
            existing_film = (
                session.query(Film)
                .filter_by(title_original=film_data["title_original"])
                .first()
            )

            if existing_film is None:
                actors_data = film_data.pop("actors", [])
                genres_data = film_data.pop("genres", [])
                actors = []
                genres = []

                for actor_name in actors_data:
                    actor = all_actors.get(actor_name)
                    if actor is None:
                        actor = Actor(name=actor_name)
                        all_actors[actor_name] = actor
                        films_to_create.append(actor)
                    actors.append(actor)

                for genre_name in genres_data:
                    genre = all_genres.get(genre_name)
                    if genre is None:
                        genre = Genre(name=genre_name)
                        all_genres[genre_name] = genre
                        films_to_create.append(genre)
                    genres.append(genre)

                film = film_schema.load(film_data, session=session)
                film.actors = actors
                film.genres = genres
                films_to_create.append(film)

        session.add_all(films_to_create)
        session.commit()
        return len(films_to_create)
