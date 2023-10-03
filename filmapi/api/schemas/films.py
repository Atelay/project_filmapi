from marshmallow_sqlalchemy.fields import Nested
from filmapi.extensions import ma, db
from filmapi.models import Film


class FilmSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Film
        exclude = ["id"]
        include_fk = True
        load_instance = True
        sqla_session = db.session

    actors = Nested(
        "ActorSchema", many=True, exclude=("films", "id", "birthday", "is_active")
    )
    genres = Nested("GenreSchema", many=True, exclude=("films", "id"))
