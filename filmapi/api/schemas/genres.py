from filmapi.extensions import ma, db
from marshmallow_sqlalchemy.fields import Nested

from filmapi.models import Genre


class GenreSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Genre
        load_instance = True
        include_fk = True
        sqla_session = db.session

    films = Nested("FilmSchema", many=True)
