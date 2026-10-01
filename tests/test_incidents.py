import pytest

BASE = "/api/v1/incidents"
INCIDENT = {"title": "Error al ingresar", "description": "La pagina muestra un error"}


def test_summary_requires_authentication(client):
    assert client.get(f"{BASE}/summary").status_code == 401


def test_empty_summary(client):
    headers, _ = login(client, "owner")
    response = client.get(f"{BASE}/summary", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"total": 0, "by_status": {"pending": 0, "done": 0, "rejected": 0}}


def test_summary_counts_and_user_isolation(client):
    owner, _ = login(client, "owner")
    other, _ = login(client, "other")
    for state in ["pending", "pending", "done", "rejected"]:
        assert client.post(BASE, json={**INCIDENT, "status": state}, headers=owner).status_code == 201
    client.post(BASE, json={**INCIDENT, "status": "done"}, headers=other)
    assert client.get(f"{BASE}/summary", headers=owner).json() == {
        "total": 4, "by_status": {"pending": 2, "done": 1, "rejected": 1},
    }
    assert client.get(f"{BASE}/summary", headers=other).json() == {
        "total": 1, "by_status": {"pending": 0, "done": 1, "rejected": 0},
    }


def login(client, username):
    password = "secret-password-123"
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": password,
        },
    )
    assert response.status_code == 201
    token = client.post(
        "/api/v1/auth/login", data={"username": username, "password": password}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}, response.json()["id"]


def test_incident_crud(client):
    headers, user_id = login(client, "owner")
    response = client.post(BASE, json=INCIDENT, headers=headers)
    assert response.status_code == 201
    incident = response.json()
    assert incident["user_id"] == user_id
    assert incident["status"] == "pending"
    assert incident["priority"] == "low"
    assert incident["created_at"] and incident["updated_at"]
    url = f"{BASE}/{incident['id']}"
    assert client.get(url, headers=headers).json() == incident
    assert client.get(BASE, headers=headers).json() == [incident]
    replacement = {
        **INCIDENT,
        "title": "Actualizada",
        "status": "done",
        "priority": "high",
    }
    response = client.put(url, json=replacement, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "done"
    assert response.json()["priority"] == "high"
    assert response.json()["title"] == "Actualizada"
    assert client.get(url, headers=headers).json()["status"] == "done"
    assert response.json()["user_id"] == user_id
    assert client.delete(url, headers=headers).status_code == 204
    assert client.get(url, headers=headers).status_code == 404
    assert client.get(BASE, headers=headers).json() == []


def test_user_isolation(client):
    owner, _ = login(client, "owner")
    other, _ = login(client, "other")
    incident = client.post(BASE, json=INCIDENT, headers=owner).json()
    url = f"{BASE}/{incident['id']}"
    assert client.get(BASE, headers=other).json() == []
    assert client.get(url, headers=other).status_code == 404
    assert (
        client.put(url, json={**INCIDENT, "title": "Hack"}, headers=other).status_code
        == 404
    )
    assert client.delete(url, headers=other).status_code == 404
    assert client.get(url, headers=owner).json()["title"] == INCIDENT["title"]


@pytest.mark.parametrize(
    "method,path,body",
    [
        ("GET", BASE, None),
        ("POST", BASE, INCIDENT),
        ("GET", f"{BASE}/1", None),
        ("PUT", f"{BASE}/1", INCIDENT),
        ("DELETE", f"{BASE}/1", None),
    ],
)
def test_authentication_required(client, method, path, body):
    assert client.request(method, path, json=body).status_code == 401


@pytest.mark.parametrize(
    "changes",
    [
        {"title": "   "},
        {"description": "x" * 10001},
        {"title": "x" * 101},
        {"status": "invalid"},
        {"user_id": 999},
        {"priority": "invalid"},
    ],
)
def test_invalid_incident(client, changes):
    headers, _ = login(client, "owner")
    assert (
        client.post(BASE, json={**INCIDENT, **changes}, headers=headers).status_code
        == 422
    )


def test_pagination(client):
    headers, _ = login(client, "owner")
    ids = [
        client.post(BASE, json={**INCIDENT, "title": str(i)}, headers=headers).json()[
            "id"
        ]
        for i in range(3)
    ]
    response = client.get(f"{BASE}?offset=1&limit=1", headers=headers)
    assert [incident["id"] for incident in response.json()] == [ids[1]]
    assert client.get(f"{BASE}?limit=101", headers=headers).status_code == 422
    assert client.get(f"{BASE}?offset=-1", headers=headers).status_code == 422


@pytest.mark.parametrize("method", ["GET", "PUT", "DELETE"])
def test_nonexistent_incident(client, method):
    headers, _ = login(client, "owner")
    assert (
        client.request(
            method,
            f"{BASE}/999",
            json=INCIDENT if method == "PUT" else None,
            headers=headers,
        ).status_code
        == 404
    )
