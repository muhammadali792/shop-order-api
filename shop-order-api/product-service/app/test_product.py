import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_get_products_empty():
    response = client.get("/products")
    assert response.status_code == 200
    assert response.json()["total"] == 0

def test_get_product_not_found():
    response = client.get("/products/999")
    assert response.status_code == 404

def test_create_product_unauthorized():
    response = client.post("/products", json={
        "name":  "Test Product",
        "price": 99.99,
        "stock": 10
    })
    assert response.status_code == 401

@patch("app.auth.httpx.AsyncClient")
async def test_create_product_as_admin(mock_client):
    mock_client.return_value.__aenter__.return_value.get = AsyncMock(
        return_value=AsyncMock(status_code=200, json=lambda: {
            "id": 1, "is_admin": True
        })
    )
    response = client.post(
        "/products",
        json={"name": "Test", "price": 9.99, "stock": 5},
        headers={"Authorization": "Bearer faketoken"}
    )
    assert response.status_code == 201
