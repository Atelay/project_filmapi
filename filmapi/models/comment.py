from datetime import datetime
import sqlalchemy
from filmapi.extensions import db


db: sqlalchemy


class Comments(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    film_id = db.Column(db.Integer, db.ForeignKey("films.id"), nullable=False)
    user = db.relationship("User", backref="comments")
    film = db.relationship("Film", backref="comments")
