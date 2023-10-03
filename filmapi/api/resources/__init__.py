from filmapi.api.resources.user import UserResource, UserList
from filmapi.api.resources.genres import GenreResource
from filmapi.api.resources.films import FilmResource, FilmListResource
from filmapi.api.resources.actors import ActorResource, ActorListResource
from filmapi.api.resources.comments import CommentResource
from filmapi.api.resources.populate_db import PopulateDbResource
from filmapi.api.resources.search import SearchResource


__all__ = [
    "UserResource",
    "UserList",
    "GenreResource",
    "FilmResource",
    "FilmListResource",
    "ActorResource",
    "ActorListResource",
    "CommentResource",
    "PopulateDbResource",
    "SearchResource",
]
