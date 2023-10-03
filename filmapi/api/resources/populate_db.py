from flask_restful import Resource, request
from flask_jwt_extended import jwt_required

from filmapi.extensions import db, es
from filmapi.models import Film, Actor, Genre, MoviesActors, MoviesGenres, Comments
from filmapi.tasks.parser import parse_imdb_data


class PopulateDbResource(Resource):
    """
    Populate Database Resource

    ---
    get:
      tags:
        - database
      summary: Populate the database with movies
      description: Populate the database with movies by scraping movie data.
      responses:
        200:
          description: Database populated successfully.
        500:
          description: Internal server error

    post:
      tags:
        - database
      summary: Add a single movie to the database
      description: Add a single movie to the database by providing a movie link in the request body.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                link:
                  type: string
              required:
                - link
      responses:
        200:
          description: Movie added successfully.
        400:
          description: Bad request, invalid movie link provided.
        500:
          description: Internal server error

    delete:
      tags:
        - database
      summary: Clear the database
      description: Clear all data from the database, including movies, actors, and genres.
      responses:
        204:
          description: Database cleared successfully.
        500:
          description: Internal server error
    """

    @jwt_required()
    def get(self):
        parse_imdb_data.delay()
        return {"message": "Database population task started."}

    @jwt_required()
    def post(self):
        link = request.get_json().get("link")
        parse_imdb_data.delay(link)
        return {"message": f"Film parsing task started for URL: {link}"}

    @jwt_required()
    def delete(self):
        es.indices.delete(index="films")
        db.session.query(MoviesActors).delete()
        db.session.query(MoviesGenres).delete()
        db.session.query(Comments).delete()
        db.session.query(Actor).delete()
        db.session.query(Genre).delete()
        db.session.query(Film).delete()
        db.session.commit()
        return "", 204
