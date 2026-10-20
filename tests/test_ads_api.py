import pytest

from app import create_app
from app.config import Config
from app.extensions import db


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
    JWT_SECRET_KEY = "test-secret-key-that-is-at-least-32-bytes-long"


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def _register_and_login(client, email="a@example.com", password="secret123"):
    client.post("/auth/register", json={"email": email, "password": password})
    r = client.post("/auth/login", json={"email": email, "password": password})
    return r.get_json()["access_token"]


def test_register_and_login(client):
    r = client.post("/auth/register", json={"email": "u@example.com", "password": "secret123"})
    assert r.status_code == 201
    assert r.get_json()["email"] == "u@example.com"

    r = client.post("/auth/login", json={"email": "u@example.com", "password": "secret123"})
    assert r.status_code == 200
    assert "access_token" in r.get_json()


def test_create_ad_requires_auth(client):
    r = client.post("/ads/", json={"title": "t", "description": "d"})
    assert r.status_code == 401


def test_create_and_get_ad(client):
    token = _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post("/ads/", json={"title": "Bike", "description": "Nice"}, headers=headers)
    assert r.status_code == 201
    ad_id = r.get_json()["id"]

    r = client.get(f"/ads/{ad_id}")
    assert r.status_code == 200
    assert r.get_json()["title"] == "Bike"


def test_only_owner_can_update_or_delete(client):
    token_a = _register_and_login(client, "a@example.com")
    token_b = _register_and_login(client, "b@example.com")

    r = client.post(
        "/ads/",
        json={"title": "Bike", "description": "Nice"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    ad_id = r.get_json()["id"]

    # B intenta editar → 403
    r = client.patch(
        f"/ads/{ad_id}",
        json={"title": "Hacked"},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert r.status_code == 403

    # B intenta borrar → 403
    r = client.delete(f"/ads/{ad_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert r.status_code == 403

    # A sí puede editar
    r = client.patch(
        f"/ads/{ad_id}",
        json={"title": "Bike v2"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert r.status_code == 200
    assert r.get_json()["title"] == "Bike v2"


def test_delete_owner(client):
    token = _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    ad_id = client.post("/ads/", json={"title": "t", "description": "d"}, headers=headers).get_json()["id"]

    r = client.delete(f"/ads/{ad_id}", headers=headers)
    assert r.status_code == 204

    r = client.get(f"/ads/{ad_id}")
    assert r.status_code == 404