"""
12 — Testing: Part 1 — TestClient Basics

Run:
    pytest examples/12_testing/test_01_basics.py -v

What this file teaches:
    - How to use FastAPI's TestClient to test endpoints without starting a server
    - How to write basic pytest test functions
    - How to assert status codes and response bodies
    - How to test different HTTP methods (GET, POST, PATCH, DELETE)
    - How to test query parameters and path parameters
    - How to test error responses (404, 422)

Key idea:
    TestClient drives the app in-process — no sockets, no server needed.
    It wraps httpx under the hood and behaves like a real HTTP client.
"""

from fastapi import FastAPI, HTTPException, Query

# ============================================================================
# A small self-contained app to test against.
# In real projects, you would import the app from your main module.
# ============================================================================

app = FastAPI(title="Test Basics Demo")

# In-memory storage for this demo (no database needed).
ITEMS: dict[int, dict] = {}
_next_id = 1


@app.get("/")
def root():
    """Root endpoint returning a welcome message."""
    return {"message": "Hello, testing!"}


@app.get("/items")
def list_items(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=50),
):
    """Return a paginated list of items."""
    all_items = list(ITEMS.values())
    return all_items[skip : skip + limit]


@app.post("/items", status_code=201)
def create_item(item: dict):
    """Create a new item and return it with an assigned id."""
    global _next_id
    item["id"] = _next_id
    ITEMS[_next_id] = item
    _next_id += 1
    return item


@app.get("/items/{item_id}")
def get_item(item_id: int):
    """Return a single item by id."""
    if item_id not in ITEMS:
        raise HTTPException(status_code=404, detail="Item not found")
    return ITEMS[item_id]


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    """Delete an item by id."""
    if item_id not in ITEMS:
        raise HTTPException(status_code=404, detail="Item not found")
    del ITEMS[item_id]


# ============================================================================
# Tests
# ============================================================================

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def reset_state():
    """
    Reset the in-memory store before each test.

    autouse=True means this fixture runs automatically for every test
    in this file — no need to pass it as an argument.

    This guarantees test isolation: each test starts with a clean slate.
    """
    global _next_id
    ITEMS.clear()
    _next_id = 1
    yield
    # Teardown (if needed) would go after yield.


@pytest.fixture(name="client")
def client_fixture():
    """
    Create a TestClient for the app.

    TestClient wraps the app so we can call endpoints
    without starting an actual server.
    """
    return TestClient(app)


# --- GET / ---

def test_root_returns_200(client):
    """The root endpoint should return 200 and a welcome message."""
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, testing!"}


# --- POST /items ---

def test_create_item(client):
    """POST /items should create an item and return 201."""
    response = client.post("/items", json={"name": "Sword", "power": 10})

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Sword"
    assert data["power"] == 10
    assert data["id"] == 1  # first item gets id=1


def test_create_multiple_items(client):
    """Each new item gets an incrementing id."""
    client.post("/items", json={"name": "Shield"})
    response = client.post("/items", json={"name": "Bow"})

    assert response.json()["id"] == 2


# --- GET /items ---

def test_list_items_empty(client):
    """GET /items on an empty store returns an empty list."""
    response = client.get("/items")

    assert response.status_code == 200
    assert response.json() == []


def test_list_items_after_create(client):
    """GET /items returns all created items."""
    client.post("/items", json={"name": "Sword"})
    client.post("/items", json={"name": "Shield"})

    response = client.get("/items")
    items = response.json()

    assert len(items) == 2
    assert items[0]["name"] == "Sword"
    assert items[1]["name"] == "Shield"


def test_list_items_pagination(client):
    """Query params skip and limit control pagination."""
    # Create 5 items.
    for i in range(5):
        client.post("/items", json={"name": f"Item {i}"})

    # Get items 2 and 3 (skip first 2, take 2).
    response = client.get("/items", params={"skip": 2, "limit": 2})
    items = response.json()

    assert len(items) == 2
    assert items[0]["name"] == "Item 2"
    assert items[1]["name"] == "Item 3"


# --- GET /items/{item_id} ---

def test_get_item_by_id(client):
    """GET /items/{id} returns the correct item."""
    client.post("/items", json={"name": "Sword"})

    response = client.get("/items/1")

    assert response.status_code == 200
    assert response.json()["name"] == "Sword"


def test_get_item_not_found(client):
    """GET /items/{id} returns 404 when item does not exist."""
    response = client.get("/items/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


# --- DELETE /items/{item_id} ---

def test_delete_item(client):
    """DELETE /items/{id} removes the item and returns 204."""
    client.post("/items", json={"name": "Sword"})

    response = client.delete("/items/1")
    assert response.status_code == 204

    # Verify it's actually gone.
    response = client.get("/items/1")
    assert response.status_code == 404


def test_delete_item_not_found(client):
    """DELETE /items/{id} returns 404 when item does not exist."""
    response = client.delete("/items/999")
    assert response.status_code == 404


# --- Validation Errors ---

def test_invalid_query_param(client):
    """Negative skip value should return 422 (validation error)."""
    response = client.get("/items", params={"skip": -1})
    assert response.status_code == 422
