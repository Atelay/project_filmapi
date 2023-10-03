from flask_restful import Resource, request
from marshmallow import ValidationError
from sqlalchemy.orm import joinedload
from flask_jwt_extended import jwt_required

from filmapi.models import Actor, MoviesActors
from filmapi.extensions import db, cache
from filmapi.api.schemas import ActorSchema


def key():
    return f"films:{request.url}"


class ActorListResource(Resource):
    """
    Actor List Resource

    ---
    get:
      tags:
        - actor
      summary: Get a list of actors
      description: Get a list of actors with optional pagination.
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
          description: Number of actors to retrieve per page (default is 20, maximum is 60)
      responses:
        200:
          description: List of actors
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/ActorSchema'
        400:
          description: Bad request, validation error in parameters
    post:
      tags:
        - actor
      summary: Create a new actor
      description: Create a new actor by providing actor data in the request body.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ActorSchema'
      responses:
        201:
          description: Actor created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ActorSchema'
        400:
          description: Bad request, validation error in actor data
    """

    actor_schema = ActorSchema()

    @cache.cached(key_prefix=key)
    def get(self):
        page = request.args.get("page", 0, type=int)
        offset = request.args.get("offset", 20, type=int)
        if offset > 60:
            return {"error": f"Offset must not be greater than {60}"}, 400
        actors = (
            db.session.query(Actor.id, Actor.name, Actor.birthday, Actor.is_active)
            .join(MoviesActors, MoviesActors.actor_id == Actor.id)
            .group_by(Actor.id)
            .offset(page * offset)
            .limit(offset)
        )
        return self.actor_schema.dump(actors, many=True), 200

    @jwt_required()
    def post(self):
        try:
            actor = self.actor_schema.load(request.json, session=db.session)
        except ValidationError as e:
            return {"message": str(e)}, 400
        db.session.add(actor)
        db.session.commit()
        return self.actor_schema.dump(actor), 201


class ActorResource(Resource):
    """
    Actor Resource

    ---
    get:
      tags:
        - actor
      summary: Get an actor by ID
      description: Get an actor's details by providing their ID.
      parameters:
        - in: path
          name: id
          schema:
            type: integer
          description: ID of the actor to retrieve
      responses:
        200:
          description: Actor details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ActorSchema'
        404:
          description: Actor not found

    post:
      tags:
        - actor
      summary: Create a new actor
      description: Create a new actor by providing actor data in the request body.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ActorSchema'
      responses:
        201:
          description: Actor created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ActorSchema'
        400:
          description: Bad request, validation error in actor data

    put:
      tags:
        - actor
      summary: Update an actor by ID
      description: Update actor by providing actor data in the request body or create a new actor if ID doesn't exist.
      parameters:
        - in: path
          name: id
          schema:
            type: integer
          description: ID of the actor to update (optional, creates a new actor if not present)
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ActorSchema'
      responses:
        200:
          description: Actor updated successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ActorSchema'
        400:
          description: Bad request, validation error in actor data

    patch:
      tags:
        - actor
      summary: Partially update an actor by ID
      description: Partially update an actor by providing partial actor data in the request body.
      parameters:
        - in: path
          name: id
          schema:
            type: integer
          description: ID of the actor to partially update
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ActorSchema'
      responses:
        200:
          description: Actor updated successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ActorSchema'
        400:
          description: Bad request, validation error in actor data
        404:
          description: Actor not found

    delete:
      tags:
        - actor
      summary: Delete an actor by ID
      description: Delete an actor by providing their ID.
      parameters:
        - in: path
          name: id
          schema:
            type: integer
          description: ID of the actor to delete
      responses:
        204:
          description: Actor deleted successfully
        404:
          description: Actor not found
    """

    actor_schema = ActorSchema()

    @cache.cached(key_prefix=key)
    def get(self, id: int):
        actor = (
            db.session.query(Actor)
            .filter_by(id=id)
            .options(joinedload(Actor.films))
            .first()
        )
        if not actor:
            return "", 404
        return self.actor_schema.dump(actor), 200

    @jwt_required()
    def put(self, id: int):
        actor = db.session.query(Actor).filter_by(id=id).first()
        if actor:
            try:
                actor = self.actor_schema.load(
                    request.json, instance=actor, session=db.session
                )
            except ValidationError as e:
                return {"message": str(e)}, 400
        else:
            try:
                actor = self.actor_schema.load(request.json, session=db.session)
            except ValidationError as e:
                return {"message": str(e)}, 400
        db.session.add(actor)
        db.session.commit()
        return self.actor_schema.dump(actor), 200

    @jwt_required()
    def patch(self, id: int):
        actor = db.session.query(Actor).filter_by(id=id).first()
        if not actor:
            return "", 404
        try:
            actor = self.actor_schema.load(
                request.json, instance=actor, partial=True, session=db.session
            )
        except ValidationError as e:
            return {"message": str(e)}, 400
        db.session.add(actor)
        db.session.commit()
        return self.actor_schema.dump(actor), 200

    @jwt_required()
    def delete(self, id: int):
        actor = db.session.query(Actor).filter_by(id=id).first()
        if not actor:
            return "Actor is not found", 404
        db.session.delete(actor)
        db.session.commit()
        return "", 204
