from typing import Dict

from flask import url_for, testing
from flask_sqlalchemy import SQLAlchemy

from filmapi.models import Film, Comments, User


def test_post_comment(
    client: testing.FlaskClient,
    db: SQLAlchemy,
    admin_headers: Dict[str, str],
    film: Film,
    admin_user: User,
):
    text = "Test comment text"
    comment_data = {"text": text}

    url = url_for("api.comments", uuid="invalid_uuid")
    response = client.post(url, json=comment_data, headers=admin_headers)
    assert response.status_code == 404

    url = url_for("api.comments", uuid=film.uuid)
    response = client.post(url, json=comment_data, headers=admin_headers)
    assert response.status_code == 201
    comment_in_db: Comments = db.session.query(Comments).first()
    assert comment_in_db is not None
    assert comment_in_db.text == comment_data["text"]
    assert comment_in_db.film_id == film.id
    assert comment_in_db.user_id == admin_user.id
