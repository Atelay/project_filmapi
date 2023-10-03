from marshmallow_sqlalchemy.fields import Nested
from filmapi.extensions import ma, db
from filmapi.models import Actor


class ActorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Actor
        include_fk = True
        load_instance = True
        sqla_session = db.session

    films = Nested(
        "FilmSchema",
        only=("title", "title_original", "uuid", "poster"),
        many=True,
        exclude=("actors",),
    )
