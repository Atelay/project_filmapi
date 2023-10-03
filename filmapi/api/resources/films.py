from flask_restful import Resource, request
from marshmallow import ValidationError
from sqlalchemy.orm import joinedload
from flask_jwt_extended import jwt_required

from filmapi.extensions import db, cache
from filmapi.models import Comments, Film, User
from filmapi.api.schemas import CommentSchema, FilmSchema
from filmapi.services.film_service import FilmService


def key():
    return f"films:{request.url}"


class FilmListResource(Resource):
    """
    Film Resource

    ---
    get:
      tags:
        - film
      summary: Get a list of films
      description: Get a list of films. You can filter films by various parameters.
      parameters:
        - in: query
          name: page
          schema:
            type: integer
          description: Page number for pagination (default is 0)
        - in: query
          name: offset
          schema:
            type: integer
          description: Number of films to retrieve per page (default is 20, maximum is 60)
        - in: query
          name: genre
          schema:
            type: string
          description: Filter films by genre
        - in: query
          name: year_from
          schema:
            type: integer
          description: Filter films by the release year (from)
        - in: query
          name: year_to
          schema:
            type: integer
          description: Filter films by the release year (to)
        - in: query
          name: rating_from
          schema:
            type: number
          description: Filter films by minimum rating
      responses:
        200:
          description: List of films
          content:
            application/json:
              schema:
                type: object
                properties:
                  film:
                    type: array
                    items:
                      $ref: '#/components/schemas/Film'
        400:
          description: Bad request, validation error in parameters

    post:
      tags:
        - film
      summary: Create a new film
      description: Create a new film by providing film data in the request body
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/FilmSchema'
      responses:
        201:
          description: Film created successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  film:
                    type: object
                    $ref: '#/components/schemas/FilmSchema'
        400:
          description: Bad request, validation error in film data

    """

    film_schema = FilmSchema()

    @cache.cached(key_prefix=key)
    def get(self):
        page = request.args.get("page", 0, type=int)
        offset = request.args.get("offset", 20, type=int)
        genre = request.args.get("genre", type=str)
        year_from = request.args.get("year_from", type=int)
        year_to = request.args.get("year_to", type=int)
        rating_from = request.args.get("rating_from", type=float)
        if offset > 60:
            return {"error": f"Offset must not be greater than {60}"}, 400
        if genre:
            films = FilmService.fetch_films_by_genre(
                db.session,
                genre,
                page,
                offset,
                year_from=year_from,
                year_to=year_to,
                rating_from=rating_from,
            )
        else:
            films = FilmService.fetch_all_films(
                db.session,
                page,
                offset,
                year_from=year_from,
                year_to=year_to,
                rating_from=rating_from,
            )
        return self.film_schema.dump(films, many=True), 200

    @jwt_required()
    def post(self):
        try:
            film = self.film_schema.load(request.json, session=db.session)
        except ValidationError as e:
            return {"message": str(e)}, 400
        db.session.add(film)
        db.session.commit()
        return self.film_schema.dump(film), 201


class FilmResource(Resource):
    """
    Film Resource

    ---
    get:
      tags:
        - film
      summary: Get a specific film by UUID
      description: Get a specific film by UUID.
      parameters:
        - in: path
          name: uuid
          schema:
            type: string
          description: UUID of the film to retrieve
      responses:
        200:
          description: A specific film
          content:
            application/json:
              schema:
                type: object
                properties:
                  film:
                    $ref: '#/components/schemas/FilmSchema'
                  comments:
                    type: array
                    items:
                      type: object
                      properties:
                        username:
                          type: string
                        created_at:
                          type: string
                          format: date-time
                        text:
                          type: string
        404:
          description: Film not found

    put:
      tags:
        - film
      summary: Update a film by UUID
      description: Update a film by providing film data in the request body or create a new film if UUID doesn't exist
      parameters:
        - in: path
          name: uuid
          schema:
            type: string
          description: UUID of the film to update (optional, creates a new film if not present)
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/FilmSchema'
      responses:
        200:
          description: Film updated successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  film: FilmSchema'
        400:
          description: Bad request, validation error in film data

    patch:
      tags:
        - film
      summary: Partially update a film by UUID
      description: Partially update a film by providing partial film data in the request body
      parameters:
        - in: path
          name: uuid
          schema:
            type: string
          description: UUID of the film to partially update
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/FilmSchema'
      responses:
        200:
          description: Film updated successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  film:
                    type: object
                    $ref: '#/components/schemas/FilmSchema'
        400:
          description: Bad request, validation error in film data
        404:
          description: Film not found

    delete:
      tags:
        - film
      summary: Delete a film by UUID
      description: Delete a film by providing its UUID
      parameters:
        - in: path
          name: uuid
          schema:
            type: string
          description: UUID of the film to delete
      responses:
        204:
          description: Film deleted successfully
        404:
          description: Film not found
    """

    film_schema = FilmSchema()
    comment_schema = CommentSchema()

    @cache.cached(key_prefix=key)
    def get(self, uuid: str):
        film = (
            FilmService.fetch_film_by_uuid(db.session, uuid)
            .options(joinedload(Film.actors), joinedload(Film.genres))
            .first()
        )
        try:
            comments_for_film = (
                db.session.query(Comments.text, Comments.created_at, User.username)
                .join(User, User.id == Comments.user_id)
                .filter(Comments.film_id == film.id)
                .all()
            )
            comment_data = [
                {
                    "username": comment.username,
                    "created_at": comment.created_at.isoformat(
                        sep=" ", timespec="seconds"
                    ),
                    "text": comment.text,
                }
                for comment in comments_for_film
            ]
        except AttributeError:
            pass
        if not film:
            return "", 404
        return {"film": self.film_schema.dump(film), "comments": comment_data}, 200

    @jwt_required()
    def put(self, uuid: str):
        film = (
            FilmService.fetch_film_by_uuid(db.session, uuid)
            .options(joinedload(Film.actors), joinedload(Film.genres))
            .first()
        )
        if film:
            try:
                film = self.film_schema.load(
                    request.json, instance=film, session=db.session
                )
            except ValidationError as e:
                return {"message": str(e)}, 400
        else:
            try:
                film = self.film_schema.load(request.json, session=db.session)
            except ValidationError as e:
                return {"message": str(e)}, 400

        db.session.add(film)
        db.session.commit()
        return self.film_schema.dump(film), 200

    @jwt_required()
    def patch(self, uuid: str):
        film = (
            FilmService.fetch_film_by_uuid(db.session, uuid)
            .options(joinedload(Film.actors), joinedload(Film.genres))
            .first()
        )
        if not film:
            return "", 404
        try:
            film = self.film_schema.load(
                request.json, instance=film, partial=True, session=db.session
            )
        except ValidationError as e:
            return {"message": str(e)}, 400
        db.session.add(film)
        db.session.commit()
        return self.film_schema.dump(film), 200

    @jwt_required()
    def delete(self, uuid: str):
        film = FilmService.fetch_film_by_uuid(db.session, uuid).first()
        if not film:
            return "", 404
        try:
            db.session.delete(film)
            db.session.commit()
        except Exception as e:
            print(f"Failed to delete film from database: {str(e)}")
        return "", 204
