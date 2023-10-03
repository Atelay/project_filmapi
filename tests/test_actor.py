from datetime import date
from typing import Dict
import json

from flask import url_for, testing
from factory import Factory
from flask_sqlalchemy import SQLAlchemy

from filmapi.models import Actor, Film


def test_get_actor_by_id(client: testing.FlaskClient, actor: Actor, db: SQLAlchemy):
    actor_url = url_for("api.actor_id", id=actor.id)
    response = client.get(actor_url)
    assert response.status_code == 200
    data: dict = json.loads(response.data.decode("utf-8"))
    assert data["name"] == actor.name
    assert data["birthday"] == date.strftime(actor.birthday, "%Y-%m-%d")
    assert data["is_active"] == actor.is_active
    assert len(data) == 5


def test_get_actor_not_found(client: testing.FlaskClient, actor: Actor):
    actor_url = url_for("api.actor_id", id=125)
    response = client.get(actor_url)
    assert response.status_code == 404


def test_get_all_actors(
    client: testing.FlaskClient,
    db: SQLAlchemy,
    film_factory: Factory,
    actor_factory: Factory,
):
    actors = actor_factory.create_batch(3)
    films = film_factory.create_batch(5)
    for film in films:
        film.actors = actors
    db.session.add_all(films)
    db.session.commit()

    response = client.get(url_for("api.actors"))
    assert response.status_code == 200
    answer: list[dict] = response.get_json()
    assert len(answer) == len(films[0].actors) == 3


def test_post_create_actor(
    client: testing.FlaskClient, db: SQLAlchemy, admin_headers: Dict[str, str]
):
    actor_to_create = {
        "name": "Test create actor",
        "birthday": "2023-09-26",
        "is_active": True,
    }
    response = client.post(
        url_for("api.actors"), json=actor_to_create, headers=admin_headers
    )
    assert response.status_code == 201

    created_actor: dict = response.get_json()
    assert created_actor["name"] == actor_to_create["name"]

    new_actor: Actor = (
        db.session.query(Actor).filter_by(name=actor_to_create["name"]).first()
    )
    assert new_actor is not None
    assert new_actor.name == actor_to_create["name"]


def test_put_actor_if_not_existing(
    client: testing.FlaskClient, db: SQLAlchemy, admin_headers: Dict[str, str]
):
    new_actor = {
        "name": "Test put unexisting actor",
        "birthday": "1900-01-01",
        "is_active": True,
    }
    actor_url = url_for("api.actor_id", id=10000)
    response = client.put(actor_url, json=new_actor, headers=admin_headers)
    assert response.status_code == 200

    response_data: dict = response.get_json()
    assert response_data["name"] == new_actor["name"]
    assert response_data["birthday"] == new_actor["birthday"]

    actor_in_db: Actor = (
        db.session.query(Actor).filter_by(name=new_actor["name"]).first()
    )
    assert actor_in_db is not None


def test_put_actor_if_existing(
    client: testing.FlaskClient,
    db: SQLAlchemy,
    admin_headers: Dict[str, str],
    actor: Actor,
):
    updated_actor = {
        "name": "Test put existing actor",
        "birthday": "1900-01-01",
        "is_active": True,
    }
    assert actor.name != updated_actor["name"]

    actor_url = url_for("api.actor_id", id=actor.id)
    response = client.put(actor_url, json=updated_actor, headers=admin_headers)
    assert response.status_code == 200

    response_data: dict = response.get_json()
    assert response_data["name"] == updated_actor["name"]
    assert actor.name == updated_actor["name"]

    actor_in_db: Actor = db.session.query(Actor).filter_by(id=actor.id).first()
    assert actor_in_db.name == response_data["name"]


def test_patch_existing_actor(
    client: testing.FlaskClient,
    db: SQLAlchemy,
    admin_headers: Dict[str, str],
    actor: Actor,
):
    updated_data = {"name": "new patch actor", "is_active": False}
    assert actor.is_active != updated_data["is_active"]
    actor_url = url_for("api.actor_id", id=actor.id)
    response = client.patch(actor_url, json=updated_data, headers=admin_headers)
    assert response.status_code == 200
    updated_actor: Actor = db.session.query(Actor).filter_by(id=actor.id).first()
    assert updated_actor.name == updated_data["name"]
    assert updated_actor.is_active == updated_data["is_active"]


def test_delete_actor(
    client: testing.FlaskClient,
    db: SQLAlchemy,
    actor: Actor,
    admin_headers: Dict[str, str],
):
    actor_url = url_for("api.actor_id", id=12345)
    rep = client.delete(actor_url, headers=admin_headers)
    assert rep.status_code == 404

    db.session.add(actor)
    db.session.commit()

    user_url = url_for("api.actor_id", id=actor.id)
    rep = client.delete(user_url, headers=admin_headers)
    assert rep.status_code == 204
    assert db.session.query(Film).filter_by(id=actor.id).first() is None
