from datetime import datetime, timedelta, timezone

import jwt
import pytest
from app.core.config import get_settings
from app.models.user import User

USER = {
    "username": "Tester",
    "email": "Tester@example.com",
    "password": "secret-password-123",
}


def register_and_login(client):
    assert client.post("/api/v1/auth/register", json=USER).status_code == 201
    response = client.post(
        "/api/v1/auth/login", data={"username": "Tester", "password": USER["password"]}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_register_login_me_and_hash(client):
    token = register_and_login(client)
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "tester"
    assert response.json()["email"] == "tester@example.com"
    assert "password" not in response.json()
    assert "password_hash" not in response.json()
    user = client.portal.call(load_user)
    assert user.password_hash.startswith("$argon2id$")
    assert user.password_hash != USER["password"]


async def load_user():
    return await User.get(username="tester")


@pytest.mark.parametrize(
    "changes", [{}, {"username": "other"}, {"email": "other@example.com"}]
)
def test_duplicate_registration(client, changes):
    assert client.post("/api/v1/auth/register", json=USER).status_code == 201
    assert (
        client.post("/api/v1/auth/register", json={**USER, **changes}).status_code
        == 409
    )


@pytest.mark.parametrize(
    "username,password", [("tester", "incorrect"), ("missing", "secret-password-123")]
)
def test_wrong_credentials(client, username, password):
    client.post("/api/v1/auth/register", json=USER)
    response = client.post(
        "/api/v1/auth/login", data={"username": username, "password": password}
    )
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize(
    "changes", [{"password": "short"}, {"email": "invalid"}, {"username": "bad name"}]
)
def test_registration_validation(client, changes):
    assert (
        client.post("/api/v1/auth/register", json={**USER, **changes}).status_code
        == 422
    )


def test_missing_token(client):
    assert client.get("/api/v1/auth/me").status_code == 401


@pytest.mark.parametrize(
    "kind",
    ["expired", "bad_signature", "missing_exp", "wrong_type", "bad_sub", "malformed"],
)
def test_rejected_tokens(client, kind):
    register_and_login(client)
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "1",
        "iat": now,
        "exp": now + timedelta(minutes=30),
        "type": "access",
    }
    key = get_settings().jwt_secret_key.get_secret_value()
    if kind == "expired":
        payload["exp"] = now - timedelta(seconds=1)
    elif kind == "bad_signature":
        key = "another-secret-key-for-tests-123456789"
    elif kind == "missing_exp":
        del payload["exp"]
    elif kind == "wrong_type":
        payload["type"] = "refresh"
    elif kind == "bad_sub":
        payload["sub"] = "abc"
    token = (
        "invalid"
        if kind == "malformed"
        else jwt.encode(payload, key, algorithm="HS256")
    )
    assert (
        client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
        ).status_code
        == 401
    )


async def deactivate_user():
    await User.filter(username="tester").update(is_active=False)


def test_inactive_user(client):
    token = register_and_login(client)
    client.portal.call(deactivate_user)
    assert (
        client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/v1/auth/login",
            data={"username": "tester", "password": USER["password"]},
        ).status_code
        == 401
    )
