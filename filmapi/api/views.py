from flask import Blueprint, jsonify
from flask_restful import Api
from marshmallow import ValidationError
from filmapi.api.resources import (
    UserResource,
    UserList,
    FilmResource,
    ActorResource,
    GenreResource,
    CommentResource,
    FilmListResource,
    ActorListResource,
    PopulateDbResource,
    SearchResource,
)


blueprint = Blueprint("api", __name__, url_prefix="/api/v1")
api = Api(blueprint)

api.add_resource(UserResource, "/users/<int:user_id>", endpoint="user_by_id")
api.add_resource(UserList, "/users", endpoint="users")
api.add_resource(
    FilmResource, "/films/<string:uuid>", endpoint="film_by_uuid", strict_slashes=False
)
api.add_resource(FilmListResource, "/films", endpoint="films", strict_slashes=False)
api.add_resource(
    ActorResource, "/actors/<int:id>", endpoint="actor_id", strict_slashes=False
)
api.add_resource(ActorListResource, "/actors", endpoint="actors", strict_slashes=False)
api.add_resource(GenreResource, "/genres", endpoint="genres", strict_slashes=False)
api.add_resource(
    CommentResource,
    "/films/<string:uuid>/comments",
    endpoint="comments",
    strict_slashes=False,
)
api.add_resource(
    PopulateDbResource,
    "/populate_db",
    endpoint="populate_db",
    strict_slashes=False,
)
api.add_resource(SearchResource, "/search", endpoint="search", strict_slashes=False)


@blueprint.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    """Return json error for marshmallow validation errors.

    This will avoid having to try/catch ValidationErrors in all endpoints, returning
    correct JSON response with associated HTTP 400 Status (https://tools.ietf.org/html/rfc7231#section-6.5.1)
    """
    return jsonify(e.messages), 400
