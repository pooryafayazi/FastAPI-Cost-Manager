# core/tests/test_users.py
import pytest
from core.config import Settings as AppSettings


ACCESS = AppSettings.COOKIE_ACCESS_NAME
REFRESH = AppSettings.COOKIE_REFRESH_NAME

@pytest.fixture
def seeded_user(user_factory):
    return user_factory(username="usertest", password="12345678")


def test_login_invalid_user_data_401_and_200(anon_client, user_factory):
    user_factory(username="usertest", password="12345678")
    payload = {
        "username" : "usertest",
        "password" : "test"
    }
    response = anon_client.post("/api/v1/users/login-cookie", json=payload)
    assert response.status_code == 401
    payload = {
        "username" : "test",
        "password" : "12345678"
    }
    response = anon_client.post("/api/v1/users/login-cookie", json=payload)
    assert response.status_code == 401
    payload = {
        "username" : "usertest",
        "password" : "12345678"
    }
    response = anon_client.post("/api/v1/users/login-cookie", json=payload)
    assert response.status_code == 200


"""
def test_login_valid_user_data_200(anon_client, user_factory):
    user_factory(username="usertest", password="12345678")
    payload = {
        "username" : "usertest",
        "password" : "12345678"
    }
    resp = anon_client.post("/api/v1/users/login-cookie", json=payload)
    assert resp.status_code == 200
"""
def test_login_valid_user_data_200(auth_client):
    resp = auth_client.post("/api/v1/users/login-cookie",
                         json={"username": "usertest", "password": "12345678"})
    assert resp.status_code == 200
    
    # 1) cookies on the client after the response
    assert auth_client.cookies.get(ACCESS) is not None
    assert auth_client.cookies.get(REFRESH) is not None

    # 2) Check Set-Cookie header flags
    # httpx.Headers has get_list; if not, get a single value with get.
    get_list = getattr(resp.headers, "get_list", None)
    set_cookie_headers = get_list("set-cookie") if get_list else [resp.headers.get("set-cookie")]

    # remove None
    set_cookie_headers = [h for h in set_cookie_headers if h]

    # Both cookies must be set
    assert any(f"{ACCESS}=" in h for h in set_cookie_headers)
    assert any(f"{REFRESH}=" in h for h in set_cookie_headers)

    # Security flags
    # HttpOnly logic for tokens
    assert any("HttpOnly" in h for h in set_cookie_headers)

    # SameSite depending on config (lax/none/strict)
    assert any("SameSite=Lax" in h or "SameSite=lax" in h for h in set_cookie_headers)

    # Secure=True
    # assert any("Secure" in h for h in set_cookie_headers)


def test_login_user_with_seeded_user_200(anon_client, seeded_user):
    r = anon_client.post("/api/v1/users/login-cookie",
                         json={"username": "usertest", "password": "12345678"})
    assert r.status_code == 200


def test_register_valid_user_data_201(anon_client):
    payload = {
        "username" : "poorya",
        "password" : "poorya@189",
        "password_confirm" : "poorya@189",
    }
    response = anon_client.post("/api/v1/users/register", json=payload)
    assert response.status_code == 201
