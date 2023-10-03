from typing import Dict

import mock
from flask import url_for, testing
from flask_sqlalchemy import SQLAlchemy


@mock.patch("filmapi.tasks.parser.parse_imdb_data")
def test_get_method(
    mock_parse_imdb_data,
    client: testing.FlaskClient,
    db: SQLAlchemy,
    admin_headers: Dict[str, str],
):
    response = client.get(url_for("api.populate_db"), headers=admin_headers)
    assert response.status_code == 200
    mock_parse_imdb_data.assert_not_called()
    data: dict = response.get_json()
    assert response.status_code == 200
    assert data == {"message": "Database population task started."}


@mock.patch("filmapi.tasks.parser.parse_imdb_data")
def test_post_method(
    mock_parse_imdb_data,
    client: testing.FlaskClient,
    db: SQLAlchemy,
    admin_headers: Dict[str, str],
):
    request_data = {"link": "https://example.com/movie"}
    response = client.post(
        url_for("api.populate_db"), json=request_data, headers=admin_headers
    )
    mock_parse_imdb_data.assert_not_called()
    assert response.status_code == 200
    data: dict = response.get_json()
    expected_message = f"Film parsing task started for URL: {request_data['link']}"
    assert data == {"message": expected_message}
