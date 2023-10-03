from flask import Flask
from flask_sqlalchemy import record_queries

from filmapi import api
from filmapi import auth
from filmapi import manage
from filmapi.api.resources import (
    UserList,
    UserResource,
    ActorResource,
    CommentResource,
    FilmResource,
    GenreResource,
    FilmListResource,
    ActorListResource,
    PopulateDbResource,
    SearchResource,
)
from filmapi.api.schemas import (
    GenreSchema,
    ActorSchema,
    CommentSchema,
    UserSchema,
    FilmSchema,
)
from filmapi.auth.views import login, refresh, revoke_access_token, revoke_refresh_token
from filmapi.extensions import apispec, cache, db, jwt, migrate, celery


def create_app(testing=False):
    """Application factory, used to create application"""
    app = Flask("filmapi")
    app.config.from_object("filmapi.config")
    if testing is True:
        app.config["TESTING"] = True
        app.config["CACHE_TYPE"] = "null"
    configure_extensions(app)
    configure_cli(app)
    configure_apispec(app)
    register_blueprints(app)
    init_celery(app)
    # app.after_request(sql_debug)

    with app.app_context():
        apispec.spec.components.schema("UserSchema", schema=UserSchema)
        apispec.spec.components.schema("FilmSchema", schema=FilmSchema)
        apispec.spec.components.schema("GenreSchema", schema=GenreSchema)
        apispec.spec.components.schema("ActorSchema", schema=ActorSchema)
        apispec.spec.components.schema("CommentSchema", schema=CommentSchema)

        apispec.spec.path(view=UserResource, app=app)
        apispec.spec.path(view=UserList, app=app)
        apispec.spec.path(view=login, app=app)
        apispec.spec.path(view=refresh, app=app)
        apispec.spec.path(view=revoke_access_token, app=app)
        apispec.spec.path(view=revoke_refresh_token, app=app)
        apispec.spec.path(view=CommentResource, app=app)
        apispec.spec.path(view=ActorListResource, app=app)
        apispec.spec.path(view=ActorResource, app=app)
        apispec.spec.path(view=FilmListResource, app=app)
        apispec.spec.path(view=FilmResource, app=app)
        apispec.spec.path(view=GenreResource, app=app)
        apispec.spec.path(view=PopulateDbResource, app=app)
        apispec.spec.path(view=SearchResource, app=app)
    return app


def configure_extensions(app):
    """Configure flask extensions"""
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)


def configure_cli(app):
    """Configure Flask 2.0's cli for easy entity management"""
    app.cli.add_command(manage.init)


def configure_apispec(app):
    """Configure APISpec for swagger support"""
    apispec.init_app(app, security=[{"jwt": []}])
    apispec.spec.components.security_scheme(
        "jwt", {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    )
    apispec.spec.components.schema(
        "PaginatedResult",
        {
            "properties": {
                "total": {"type": "integer"},
                "pages": {"type": "integer"},
                "next": {"type": "string"},
                "prev": {"type": "string"},
            }
        },
    )


def register_blueprints(app):
    """Register all blueprints for application"""
    app.register_blueprint(auth.views.blueprint)
    app.register_blueprint(api.views.blueprint)


def init_celery(app=None):
    app = app or create_app()
    celery.conf.update(app.config.get("CELERY", {}))

    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context"""

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def sql_debug(response):
    queries = record_queries.get_recorded_queries()
    total_duration = 0.0
    for query in queries:
        total_duration += query.duration
    print("=" * 80)
    print(
        " SQL Queries - {0} Queries Executed in {1}ms".format(
            len(queries), round(total_duration * 1000, 2)
        )
    )
    return response
