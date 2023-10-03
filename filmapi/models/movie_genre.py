import sqlalchemy

from filmapi.extensions import db


db: sqlalchemy


class MoviesGenres(db.Model):
    __tablename__ = "movies_genres"

    film_id = db.Column(db.Integer, db.ForeignKey("films.id"), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey("genres.id"), primary_key=True)
