from filmapi.extensions import ma, db
from filmapi.models import Comments


class CommentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Comments
        include_fk = True
        load_instance = True
        sqla_session = db.session
