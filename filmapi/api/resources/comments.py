from flask_restful import Resource, request

from filmapi.extensions import db
from filmapi.models import Film, Comments
from filmapi.api.schemas import CommentSchema
from flask_jwt_extended import jwt_required, get_current_user


class CommentResource(Resource):
    """
    Comment Resource

    ---
    post:
      tags:
        - comments
      summary: Add a comment to a movie
      description: Add a comment to a movie by providing the movie's UUID and the comment text in the request body.
      parameters:
        - in: path
          name: uuid
          schema:
            type: string
          required: true
          description: UUID of the movie to comment on.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                text:
                  type: string
              required:
                - text
      responses:
        201:
          description: Comment added successfully.
        404:
          description: Movie not found.
        500:
          description: Internal server error
    """

    comment_schema = CommentSchema()

    @jwt_required()
    def post(self, uuid: str):
        user = get_current_user()
        film = db.session.query(Film).filter_by(uuid=uuid).first()
        if not film:
            return {"message": "Film not found"}, 404
        new_comment = Comments(text=request.json["text"], user=user, film=film)
        db.session.add(new_comment)
        db.session.commit()
        return "ok", 201
