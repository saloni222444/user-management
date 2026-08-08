"""End-to-end tests for the User Management API, run against a real MySQL
test database (see conftest.py) via the Flask test client."""


def create_user(client, name="Saloni", email="saloni@example.com", role="Developer"):
    return client.post("/users", json={"name": name, "email": email, "role": role})


# ---------------------------------------------------------------------------
# GET /users
# ---------------------------------------------------------------------------

def test_get_users_empty(client):
    resp = client.get("/users")
    body = resp.get_json()

    assert resp.status_code == 200
    assert body["success"] is True
    assert body["data"] == []
    assert body["pagination"]["total"] == 0


# ---------------------------------------------------------------------------
# POST /users - success and validation
# ---------------------------------------------------------------------------

def test_post_user_valid(client):
    resp = create_user(client)
    body = resp.get_json()

    assert resp.status_code == 201
    assert body["success"] is True
    assert body["data"]["name"] == "Saloni"
    assert body["data"]["email"] == "saloni@example.com"
    assert body["data"]["role"] == "Developer"
    assert isinstance(body["data"]["id"], int)


def test_post_user_missing_name(client):
    resp = client.post("/users", json={"email": "a@example.com", "role": "Developer"})
    body = resp.get_json()

    assert resp.status_code == 400
    assert body["success"] is False
    assert body["error"] == "Name is required"


def test_post_user_missing_email(client):
    resp = client.post("/users", json={"name": "Saloni", "role": "Developer"})
    body = resp.get_json()

    assert resp.status_code == 400
    assert body["error"] == "Email is required"


def test_post_user_missing_role(client):
    resp = client.post("/users", json={"name": "Saloni", "email": "a@example.com"})
    body = resp.get_json()

    assert resp.status_code == 400
    assert body["error"] == "Role is required"


def test_post_user_invalid_email(client):
    resp = client.post(
        "/users", json={"name": "Saloni", "email": "wrong-email", "role": "Developer"}
    )
    body = resp.get_json()

    assert resp.status_code == 400
    assert body["error"] == "Invalid email format"


def test_post_user_duplicate_email(client):
    first = create_user(client, name="Saloni", email="dup@example.com")
    assert first.status_code == 201

    second = create_user(client, name="Someone Else", email="dup@example.com")
    body = second.get_json()

    assert second.status_code == 409
    assert body["success"] is False
    assert body["error"] == "Email already exists"


def test_post_user_duplicate_email_case_insensitive(client):
    create_user(client, email="Case@Example.com")
    second = create_user(client, email="case@example.com")

    assert second.status_code == 409


# ---------------------------------------------------------------------------
# GET /users/<id>
# ---------------------------------------------------------------------------

def test_get_existing_user(client):
    created = create_user(client).get_json()["data"]

    resp = client.get(f"/users/{created['id']}")
    body = resp.get_json()

    assert resp.status_code == 200
    assert body["success"] is True
    assert body["data"] == created


def test_get_nonexistent_user(client):
    resp = client.get("/users/999999")
    body = resp.get_json()

    assert resp.status_code == 404
    assert body["success"] is False
    assert body["error"] == "User not found"


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def test_search_by_name(client):
    create_user(client, name="Saloni Sharma", email="saloni@example.com")
    create_user(client, name="Rahul Verma", email="rahul@example.com")

    resp = client.get("/users?search=saloni")
    body = resp.get_json()

    assert resp.status_code == 200
    assert len(body["data"]) == 1
    assert body["data"][0]["name"] == "Saloni Sharma"


def test_search_by_email(client):
    create_user(client, name="Saloni", email="saloni@gmail.com")
    create_user(client, name="Rahul", email="rahul@yahoo.com")

    resp = client.get("/users?search=gmail")
    body = resp.get_json()

    assert resp.status_code == 200
    assert len(body["data"]) == 1
    assert body["data"][0]["email"] == "saloni@gmail.com"


def test_search_is_case_insensitive(client):
    create_user(client, name="Saloni", email="saloni@example.com")

    resp = client.get("/users?search=SALONI")
    body = resp.get_json()

    assert len(body["data"]) == 1


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

def test_pagination(client):
    for i in range(25):
        create_user(client, name=f"User {i}", email=f"user{i}@example.com")

    resp = client.get("/users?page=1&limit=10")
    body = resp.get_json()

    assert resp.status_code == 200
    assert len(body["data"]) == 10
    assert body["pagination"] == {"page": 1, "limit": 10, "total": 25, "pages": 3}

    resp_page3 = client.get("/users?page=3&limit=10")
    body_page3 = resp_page3.get_json()
    assert len(body_page3["data"]) == 5


def test_pagination_defaults(client):
    for i in range(3):
        create_user(client, name=f"User {i}", email=f"user{i}@example.com")

    resp = client.get("/users")
    body = resp.get_json()

    assert body["pagination"]["page"] == 1
    assert body["pagination"]["limit"] == 10


def test_invalid_pagination_params(client):
    for query in ["page=0", "limit=0", "page=-1", "limit=-5", "page=abc", "limit=xyz"]:
        resp = client.get(f"/users?{query}")
        body = resp.get_json()

        assert resp.status_code == 400, query
        assert body["success"] is False
        assert body["error"] == "Invalid pagination parameters"


def test_pagination_limit_is_capped(client):
    resp = client.get("/users?limit=1000")
    body = resp.get_json()

    assert resp.status_code == 200
    assert body["pagination"]["limit"] == 100


# ---------------------------------------------------------------------------
# JSON error responses / unexpected requests
# ---------------------------------------------------------------------------

def test_unknown_route_returns_json_404(client):
    resp = client.get("/does-not-exist")
    body = resp.get_json()

    assert resp.status_code == 404
    assert body["success"] is False
    assert "error" in body


def test_method_not_allowed_returns_json(client):
    resp = client.delete("/users")
    body = resp.get_json()

    assert resp.status_code == 405
    assert body["success"] is False
    assert "error" in body


def test_post_with_empty_body_returns_validation_error(client):
    resp = client.post("/users", json={})
    body = resp.get_json()

    assert resp.status_code == 400
    assert body["success"] is False


def test_post_with_malformed_json_is_handled(client):
    resp = client.post(
        "/users", data="{not valid json", content_type="application/json"
    )
    body = resp.get_json()

    assert resp.status_code == 400
    assert body["success"] is False
