import sqlalchemy

from filmapi.extensions import db


db: sqlalchemy


class MoviesActors(db.Model):
    __tablename__ = "movies_actors"

    actor_id = db.Column(db.Integer, db.ForeignKey("actors.id"), primary_key=True)
    film_id = db.Column(db.Integer, db.ForeignKey("films.id"), primary_key=True)
