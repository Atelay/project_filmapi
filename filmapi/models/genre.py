import sqlalchemy
from filmapi.extensions import db


db: sqlalchemy


class Genre(db.Model):
    __tablename__ = "genres"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"Genre({self.name})"
