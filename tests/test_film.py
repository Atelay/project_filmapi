import json
from typing import Dict, List

from flask import url_for, testing
from flask_sqlalchemy import SQLAlchemy
from factory import Factory

from filmapi.models import Genre, Film
from filmapi.services.film_service import FilmService


def test_get_film_by_uuid(client: testing.FlaskClient, film: Film, db: SQLAlchemy):
    film_url = url_for("api.film_by_uuid", uuid=film.uuid)
    response = client.get(film_url)
    assert response.status_code == 200
    data = json.loads(response.data.decode("utf-8"))
    assert data["film"]["title"] == film.title
    assert data["film"]["rating"] == film.rating
    assert len(data["film"]) == 13


def test_get_film_not_found(client: testing.FlaskClient, film: Film):
    film_url = url_for("api.film_by_uuid", uuid="invalid-uuid")
    response = client.get(film_url)
    assert response.status_code == 404


def test_get_all_films(
    client: testing.FlaskClient, db: SQLAlchemy, film_factory: Factory
):
    genres = [Genre(name="Drama"), Genre(name="Adventure")]
    films: List[Film] = film_factory.create_batch(5)
    for film in films:
        film.genres = genres
    db.session.add_all(films)
    db.session.commit()

    response_with_genre = client.get(url_for("api.films", genre="Crime"))
    assert response_with_genre.status_code == 200
    answer_without_result = response_with_genre.get_json()
    assert len(answer_without_result) == 0

    response = client.get(url_for("api.films"))
    assert response.status_code == 200
    answer: dict = response.get_json()
    assert len(answer) == len(films)
    assert all(len(data) == 7 for data in answer)
    for input_data, output_data in zip(films, answer):
        assert input_data.uuid == output_data["uuid"]
        assert input_data.title == output_data["title"]


def test_post_create_film(
    client: testing.FlaskClient, db: SQLAlchemy, admin_headers: Dict[str, str]
):
    film_to_create = {
        "title": "Test create film",
        "title_original": "Original Title",
        "poster": "poster_url",
        "rating": 1.0,
        "description": "Film description",
        "release_date": "2023-09-26",
        "budget": "Budget",
        "distributed_by": "Distributor",
        "length": 120,
        "trailer": "trailer_url",
    }
    response = client.post(
        url_for("api.films"), json=film_to_create, headers=admin_headers
    )
    assert response.status_code == 201

    created_film: dict = response.get_json()
    assert created_film["title"] == film_to_create["title"]
    assert created_film["rating"] == film_to_create["rating"]

    new_film: Film = (
        db.session.query(Film).filter_by(title=film_to_create["title"]).first()
    )
    assert new_film is not None
    assert new_film.title == film_to_create["title"]


def test_put_film_if_not_existing(
    client: testing.FlaskClient, db: SQLAlchemy, admin_headers: Dict[str, str]
):
    data = {
        "title": "New disgusting Film",
        "title_original": "Original Title",
        "poster": "poster_url",
        "rating": 2.5,
        "description": "Film description",
        "release_date": "2023-09-26",
        "budget": "Budget",
        "distributed_by": "Distributor",
        "length": 120,
        "trailer": "trailer_url",
    }
    film_url = url_for("api.film_by_uuid", uuid="nonexistent uuid")
    response = client.put(film_url, json=data, headers=admin_headers)
    assert response.status_code == 200

    data: dict = response.get_json()
    assert data["title"] == "New disgusting Film"
    assert data["rating"] == 2.5

    new_film: Film = (
        db.session.query(Film).filter_by(title="New disgusting Film").first()
    )
    assert new_film is not None


def test_put_film_if_existing(
    client: testing.FlaskClient,
    db: SQLAlchemy,
    admin_headers: Dict[str, str],
    film: Film,
):
    updated_movie = {
        "title": "Updated title",
        "title_original": "Updated original title",
        "poster": "poster_url",
        "rating": 2.5,
        "description": "Film description",
        "release_date": "2023-09-26",
        "budget": "Budget",
        "distributed_by": "Distributor",
        "length": 120,
        "trailer": "trailer_url",
    }
    film_url = url_for("api.film_by_uuid", uuid=film.uuid)
    response = client.put(film_url, json=updated_movie, headers=admin_headers)
    assert response.status_code == 200

    response_data: dict = response.get_json()
    assert response_data["title"] == updated_movie["title"]
    assert response_data["title_original"] == updated_movie["title_original"]
    assert response_data["trailer"] == film.trailer
    assert response_data["uuid"] == film.uuid

    updated_film: Film = FilmService.fetch_film_by_uuid(db.session, film.uuid).first()
    assert updated_film.title == response_data["title"]
    assert updated_film.title_original == response_data["title_original"]


def test_patch_existing_film(
    client: testing.FlaskClient,
    db: SQLAlchemy,
    admin_headers: Dict[str, str],
    film: Film,
):
    updated_data = {
        "description": "testing movie update using patch method",
        "rating": 9.9,
    }
    film_url = url_for("api.film_by_uuid", uuid=film.uuid)
    response = client.patch(film_url, json=updated_data, headers=admin_headers)
    assert response.status_code == 200
    updated_film: Film = db.session.query(Film).filter_by(uuid=film.uuid).first()
    assert updated_film.description == updated_data["description"]
    assert updated_film.rating == updated_data["rating"]
    assert updated_film.title == film.title


def test_delete_film(
    client: testing.FlaskClient,
    db: SQLAlchemy,
    film: Film,
    admin_headers: Dict[str, str],
):
    film_url = url_for("api.film_by_uuid", uuid="invalid-uuid")
    rep = client.delete(film_url, headers=admin_headers)
    assert rep.status_code == 404

    db.session.add(film)
    db.session.commit()

    user_url = url_for("api.film_by_uuid", uuid=film.uuid)
    rep = client.delete(user_url, headers=admin_headers)
    assert rep.status_code == 204
    assert db.session.query(Film).filter_by(uuid=film.uuid).first() is None
