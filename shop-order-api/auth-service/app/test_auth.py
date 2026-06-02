import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_register():
    response = client.post("/auth/register", json={
        "email":    "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

def test_login():
    response = client.post("/auth/login", json={
        "email":    "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password():
    response = client.post("/auth/login", json={
        "email":    "test@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
