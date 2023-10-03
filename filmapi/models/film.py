import sqlalchemy
from sqlalchemy import event

from uuid import uuid4

from filmapi.extensions import db, es


db: sqlalchemy


class Film(db.Model):
    __tablename__ = "films"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    title_original = db.Column(db.String, nullable=False)
    release_date = db.Column(db.Date, index=True, nullable=False)
    uuid = db.Column(db.String(36), unique=True)
    description = db.Column(db.Text)
    distributed_by = db.Column(db.String(128), nullable=False)
    length = db.Column(db.Float)
    rating = db.Column(db.Float)
    budget = db.Column(db.String)
    poster = db.Column(db.String)
    trailer = db.Column(db.String)
    actors = db.relationship(
        "Actor",
        secondary="movies_actors",
        lazy=True,
        backref=db.backref("films", lazy=True),
    )
    genres = db.relationship(
        "Genre",
        secondary="movies_genres",
        lazy=True,
        backref=db.backref("films", lazy=True),
    )

    def __init__(
        self,
        title,
        poster,
        trailer,
        budget,
        title_original,
        release_date,
        description,
        distributed_by,
        length,
        rating,
        actors=None,
        genres=None,
    ):
        self.title = title
        self.title_original = title_original
        self.release_date = release_date
        self.uuid = str(uuid4())
        self.description = description
        self.distributed_by = distributed_by
        self.budget = budget
        self.length = length
        self.rating = rating
        self.poster = poster
        self.trailer = trailer
        if not actors:
            self.actors = []
        else:
            self.actors = actors
        if not genres:
            self.genres = []
        else:
            self.genres = genres

    def __repr__(self):
        return f"Film({self.title}, {self.title_original}, {self.release_date}, {self.uuid}"

    @staticmethod
    def after_insert(mapper, connection, target: type["Film"]):
        doc = {
            "title": target.title,
            "title_original": target.title_original,
            "release_date": target.release_date,
            "uuid": target.uuid,
            "description": target.description,
            "distributed_by": target.distributed_by,
            "length": target.length,
            "rating": target.rating,
            "budget": target.budget,
            "poster": target.poster,
            "trailer": target.trailer,
        }
        es.index(index="films", body=doc)

    @staticmethod
    def after_delete(mapper, connection, target: type["Film"]):
        es.delete_by_query(
            index="films", body={"query": {"match": {"uuid": target.uuid}}}
        )


event.listen(Film, "after_insert", Film.after_insert)
event.listen(Film, "after_delete", Film.after_delete)
