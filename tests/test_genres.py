from typing import Dict

from flask import url_for, testing
from flask_sqlalchemy import SQLAlchemy


def test_get_genres(
    client: testing.FlaskClient, db: SQLAlchemy, admin_headers: Dict[str, str]
):
    film = {
        "title": "Test Film 1",
        "title_original": "Original Title",
        "poster": "poster_url",
        "rating": 7.5,
        "description": "Film description",
        "release_date": "2023-09-26",
        "actors": [{"name": "Actor 1"}, {"name": "Actor 2"}],
        "genres": [{"name": "Genre 1"}, {"name": "Genre 2"}],
        "budget": "Budget",
        "distributed_by": "Distributor",
        "length": 120,
        "trailer": "trailer_url",
    }
    response = client.get(url_for("api.genres"))
    data: dict = response.get_json()
    assert response.status_code == 200
    assert len(data) == 0

    response = client.post(url_for("api.films"), json=film, headers=admin_headers)
    assert response.status_code == 201

    new_response = client.get(url_for("api.genres"))
    data: dict = new_response.get_json()
    assert new_response.status_code == 200
    assert len(data) == 2
    for genre, resp in zip(film["genres"], data):
        assert genre["name"] == resp["name"]
