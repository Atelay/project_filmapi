from flask_restful import Resource
from filmapi.models import Genre, MoviesGenres
from filmapi.extensions import db, cache
from filmapi.api.schemas import GenreSchema


class GenreResource(Resource):
    """
    Genre Resource

    ---
    get:
      tags:
        - genre
      summary: Get a list of movie genres
      description: Get a list of movie genres.
      responses:
        200:
          description: List of movie genres
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
                  properties:
                    id:
                      type: integer
                    name:
                      type: string
        404:
          description: No genres found
    """

    genre_schema = GenreSchema()

    @cache.cached()
    def get(self):
        genres = (
            db.session.query(Genre.id, Genre.name)
            .join(MoviesGenres, MoviesGenres.genre_id == Genre.id)
            .group_by(Genre.id)
            .all()
        )
        return self.genre_schema.dump(genres, many=True), 200
