"""
12 — Testing: Part 2 — Database Testing with Dependency Override

Run:
    pytest examples/12_testing/test_02_database.py -v

What this file teaches:
    - How to use app.dependency_overrides to swap the real DB for a test DB
    - How to create an in-memory SQLite database using StaticPool
    - How to write pytest fixtures with yield (setup + teardown)
    - How to ensure each test gets a fresh, isolated database
    - How to test full CRUD operations against a real database layer

Key idea:
    app.dependency_overrides lets you replace any FastAPI dependency
    at test time. This is the standard way to swap a production database
    for an in-memory test database.

    StaticPool keeps the in-memory SQLite database alive across multiple
    connections within a single test. Without it, each connection would
    create a separate empty database.
"""

from contextlib import asynccontextmanager
from typing import Annotated

import pytest
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.testclient import TestClient
from sqlmodel import Field, Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool


# ============================================================================
# Database Layer
# ============================================================================

# Production database URL (used when running the app normally).
DATABASE_URL = "sqlite:///./test_demo.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


def get_session():
    """
    Yield one database session per request.

    This is the dependency that we will OVERRIDE in tests
    to use an in-memory database instead.
    """
    with Session(engine) as session:
        yield session


# Reusable type alias for dependency injection.
SessionDep = Annotated[Session, Depends(get_session)]


# ============================================================================
# Model
# ============================================================================

class Hero(SQLModel, table=True):
    """Database table for heroes."""
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    power: str
    age: int | None = None


# ============================================================================
# App
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(title="DB Testing Demo", lifespan=lifespan)


@app.post("/heroes", status_code=201)
def create_hero(hero: dict, session: SessionDep):
    """Create a new hero."""
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


@app.get("/heroes")
def list_heroes(
    session: SessionDep,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    """Return a paginated list of heroes."""
    statement = select(Hero).offset(skip).limit(limit)
    return session.exec(statement).all()


@app.get("/heroes/{hero_id}")
def get_hero(hero_id: int, session: SessionDep):
    """Return one hero by primary key."""
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


@app.patch("/heroes/{hero_id}")
def update_hero(hero_id: int, patch: dict, session: SessionDep):
    """Partially update a hero."""
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")

    for field, value in patch.items():
        setattr(hero, field, value)

    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@app.delete("/heroes/{hero_id}", status_code=204)
def delete_hero(hero_id: int, session: SessionDep):
    """Delete a hero by primary key."""
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture(name="session")
def session_fixture():
    """
    Create a fresh in-memory SQLite database for each test.

    Why in-memory?
        - Fast: no disk I/O
        - Isolated: each test starts with empty tables
        - Clean: no leftover data between tests

    Why StaticPool?
        SQLite in-memory databases are connection-scoped.
        StaticPool ensures all connections share the SAME in-memory
        database within a single test, preventing "table not found" errors.
    """
    test_engine = create_engine(
        "sqlite://",                                    # in-memory
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,                           # single shared connection
    )

    # Create all tables in the test database.
    SQLModel.metadata.create_all(test_engine)

    with Session(test_engine) as session:
        yield session

    # Teardown: tables are destroyed when the in-memory DB is garbage collected.


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    A TestClient that uses the in-memory DB instead of the real one.

    dependency_overrides is a dict on the FastAPI app that lets you
    replace any dependency with a test version:

        app.dependency_overrides[original_dep] = replacement_dep

    After the test, we MUST call .clear() to avoid leaking overrides
    into other tests.
    """

    # This function replaces get_session during tests.
    def override_get_session():
        yield session

    # Swap the real dependency for our test version.
    app.dependency_overrides[get_session] = override_get_session

    client = TestClient(app)
    yield client

    # Always clean up overrides after the test.
    app.dependency_overrides.clear()


# ============================================================================
# Helper
# ============================================================================

def create_test_hero(client: TestClient, name: str = "Ada", power: str = "logic", age: int = 30) -> dict:
    """Helper function to create a hero and return the response data."""
    response = client.post(
        "/heroes",
        json={"name": name, "power": power, "age": age},
    )
    return response.json()


# ============================================================================
# Tests — Create
# ============================================================================

def test_create_hero(client):
    """POST /heroes should persist a hero in the database and return 201."""
    response = client.post(
        "/heroes",
        json={"name": "Ada", "power": "logic", "age": 30},
    )

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Ada"
    assert data["power"] == "logic"
    assert data["age"] == 30
    assert data["id"] is not None  # database assigned an id


def test_create_hero_without_age(client):
    """Age is optional and defaults to None."""
    response = client.post(
        "/heroes",
        json={"name": "Bob", "power": "speed"},
    )

    assert response.status_code == 201
    assert response.json()["age"] is None


# ============================================================================
# Tests — Read
# ============================================================================

def test_list_heroes_empty(client):
    """An empty database returns an empty list."""
    response = client.get("/heroes")

    assert response.status_code == 200
    assert response.json() == []


def test_list_heroes(client):
    """GET /heroes returns all created heroes."""
    create_test_hero(client, name="Ada", power="logic")
    create_test_hero(client, name="Bob", power="speed")

    response = client.get("/heroes")
    heroes = response.json()

    assert len(heroes) == 2
    names = {h["name"] for h in heroes}
    assert names == {"Ada", "Bob"}


def test_list_heroes_pagination(client):
    """skip and limit control which heroes are returned."""
    for i in range(5):
        create_test_hero(client, name=f"Hero {i}", power="power")

    response = client.get("/heroes", params={"skip": 1, "limit": 2})
    heroes = response.json()

    assert len(heroes) == 2
    assert heroes[0]["name"] == "Hero 1"
    assert heroes[1]["name"] == "Hero 2"


def test_get_hero_by_id(client):
    """GET /heroes/{id} returns the correct hero."""
    created = create_test_hero(client)

    response = client.get(f"/heroes/{created['id']}")

    assert response.status_code == 200
    assert response.json()["name"] == "Ada"


def test_get_hero_not_found(client):
    """GET /heroes/{id} returns 404 for nonexistent heroes."""
    response = client.get("/heroes/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Hero not found"


# ============================================================================
# Tests — Update
# ============================================================================

def test_update_hero(client):
    """PATCH /heroes/{id} updates only the provided fields."""
    created = create_test_hero(client, name="Ada", power="logic")
    hero_id = created["id"]

    response = client.patch(
        f"/heroes/{hero_id}",
        json={"power": "super logic"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["power"] == "super logic"
    assert data["name"] == "Ada"  # name was NOT changed


def test_update_hero_not_found(client):
    """PATCH /heroes/{id} returns 404 for nonexistent heroes."""
    response = client.patch("/heroes/999", json={"power": "x"})
    assert response.status_code == 404


# ============================================================================
# Tests — Delete
# ============================================================================

def test_delete_hero(client):
    """DELETE /heroes/{id} removes the hero from the database."""
    created = create_test_hero(client)
    hero_id = created["id"]

    # Delete the hero.
    response = client.delete(f"/heroes/{hero_id}")
    assert response.status_code == 204

    # Verify it no longer exists.
    response = client.get(f"/heroes/{hero_id}")
    assert response.status_code == 404


def test_delete_hero_not_found(client):
    """DELETE /heroes/{id} returns 404 for nonexistent heroes."""
    response = client.delete("/heroes/999")
    assert response.status_code == 404


# ============================================================================
# Tests — Isolation
# ============================================================================

def test_isolation_first(client):
    """Create a hero — this should NOT leak into the next test."""
    create_test_hero(client, name="Leak Test")
    response = client.get("/heroes")
    assert len(response.json()) == 1


def test_isolation_second(client):
    """
    This test runs AFTER test_isolation_first, but should see
    an empty database because each test gets a fresh DB.
    """
    response = client.get("/heroes")
    assert len(response.json()) == 0  # no leakage from previous test
