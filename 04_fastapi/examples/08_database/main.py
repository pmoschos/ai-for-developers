"""
08 — Database: Full CRUD App with SQLModel

Run from inside this folder:
    fastapi dev main.py

Or from the project root:
    uvicorn examples.08_database.main:app --reload

Docs: http://127.0.0.1:8000/docs
"""

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, select

from db import create_db_and_tables, get_session
from models import Hero, HeroUpdate

# --- Lifespan: create tables on startup ---


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan handler.

    This function is split into two phases:
    1. Code before `yield`  -> runs during application startup
    2. Code after `yield`   -> runs during application shutdown

    The @asynccontextmanager decorator is required so FastAPI
    can treat this function as an async context manager.
    """

    # Runs once when the application starts.
    # Here we create the database tables if they do not already exist.
    create_db_and_tables()

    # Simple confirmation message for development/debugging.
    print("Database ready [OK]")

    # The `yield` separates the startup phase from the shutdown phase.
    # While the application is running and serving requests,
    # execution is conceptually paused at this point.
    yield

    # Code after `yield` runs when the application is shutting down.
    # You can place cleanup logic here, such as closing connections,
    # releasing resources, or writing shutdown logs.
    print("Shutting down...")

# lifespan as lifespan handler in FastAPI
app = FastAPI(title="Hero API — CRUD with SQLModel", 
              description="Hero API with SQLModel",
              version="0.0.1",
              # `lifespan` (left side) is a FastAPI parameter.
              # It expects an async context manager function that defines
              # what should happen during startup and shutdown.
              #
              # `lifespan` (right side) is the function we defined earlier.
              # We pass that function to FastAPI so it can use it as the
              # application's lifecycle handler.
              lifespan=lifespan)

# Type alias for the session dependency
SessionDep = Annotated[Session, Depends(get_session)]


# --- CREATE ---

@app.post("/heroes", response_model=Hero)
def create_hero(hero: Hero, session: SessionDep):
    """
    Create a new hero.

    Request body:
    - hero: a Hero object parsed and validated from the incoming JSON body

    response_model=Hero tells FastAPI to:
    - validate the returned data
    - serialize the response using the Hero schema
    - document the response shape in OpenAPI / Swagger UI
    """

    # Add the new hero object to the current database session.
    # At this point, it is staged for insertion but not yet permanently saved.
    session.add(hero)

    # Commit the transaction so the INSERT is written to the database.
    session.commit()

    # Refresh the object from the database.
    # This is useful to load generated values such as the auto-created id.
    session.refresh(hero)

    # Return the newly created hero.
    # FastAPI will serialize it to JSON.
    return hero


# --- READ ---

@app.get("/heroes")
def list_heroes(session: SessionDep, skip: int = 0, limit: int = 20):
    """
    Return a paginated list of heroes.

    Query parameters:
    - skip: how many rows to ignore from the beginning
    - limit: maximum number of rows to return

    Example:
    /heroes?skip=0&limit=20   -> first 20 heroes
    /heroes?skip=20&limit=20  -> next 20 heroes
    """

    # Build a SELECT query for the Hero table.
    # select(Hero) means: fetch Hero rows from the database.
    statement = select(Hero)

    # Apply pagination:
    # - offset(skip): skip the first `skip` rows
    # - limit(limit): return at most `limit` rows
    statement = statement.offset(skip).limit(limit)

    # Execute the SQL query through the current session.
    # session.exec(...) returns a result object.
    results = session.exec(statement)

    # .all() collects all returned rows into a Python list.
    return results.all()

    # in one line all of the above is: 
    # return session.exec(select(Hero).offset(skip).limit(limit)).all()


@app.get("/heroes/{hero_id}", response_model=Hero)
def get_hero(hero_id: int, session: SessionDep):
    """
    Return a single hero by its ID.

    Path parameter:
    - hero_id: the primary key of the hero to retrieve

    response_model=Hero tells FastAPI to:
    - validate the returned data
    - serialize it according to the Hero schema
    - include the correct response shape in the OpenAPI docs
    """

    # session.get(Model, primary_key) is the simplest way
    # to fetch one row by its primary key.
    hero = session.get(Hero, hero_id)

    # If no row exists with this ID, return HTTP 404 Not Found.
    # This is the standard REST behavior for a missing resource.
    if not hero:
        raise HTTPException(404, "Hero not found")

    # If the hero exists, return it.
    # FastAPI will convert the SQLModel object into JSON.
    return hero


# --- UPDATE ---

@app.patch("/heroes/{hero_id}", response_model=Hero)
def update_hero(hero_id: int, patch: HeroUpdate, session: SessionDep):
    """
    Partially update an existing hero.

    PATCH is used for partial updates, meaning the client may send
    only the fields that should change.

    Example request body:
    {
        "power": "Flight"
    }

    In that case, only the `power` field is updated,
    while the other fields remain unchanged.

    model_dump(exclude_unset=True) is important because it excludes
    fields that were not provided by the client at all.
    """

    # Try to load the existing hero from the database by primary key.
    hero = session.get(Hero, hero_id)

    # If no hero exists with that ID, return HTTP 404 Not Found.
    if not hero:
        raise HTTPException(404, "Hero not found")

    # Convert the PATCH schema into a dictionary containing only
    # the fields explicitly sent in the request body.
    #
    # Example:
    # if the client sends {"age": 30},
    # the result will be {"age": 30}
    # and not include name/power/team_id.
    update_data = patch.model_dump(exclude_unset=True)

    # Apply each provided field dynamically to the existing hero object.
    # setattr(obj, field, value) is equivalent to:
    #   hero.field = value
    # but works dynamically when field names come from a dictionary.
    for field, value in update_data.items():
        setattr(hero, field, value)

    # Mark the object for persistence in the current session.
    # In many cases the object is already tracked, but session.add(hero)
    # is often kept for clarity and consistency.
    session.add(hero)

    # Commit the transaction so the changes are written to the database.
    session.commit()

    # Refresh the object from the database to ensure we return
    # the latest persisted state.
    session.refresh(hero)

    # Return the updated hero.
    # FastAPI serializes it according to response_model=Hero.
    return hero


# --- DELETE ---

@app.delete("/heroes/{hero_id}", status_code=204)
def delete_hero(hero_id: int, session: SessionDep):
    """
    Delete a hero by its ID.

    Path parameter:
    - hero_id: the primary key of the hero to delete

    status_code=204 means:
    - the deletion was successful
    - no response body is returned

    HTTP 204 No Content is a common REST choice for successful deletes.
    """

    # Fetch the hero from the database using its primary key.
    # We must first load the object before deleting it.
    hero = session.get(Hero, hero_id)

    # If no hero exists with that ID, return HTTP 404 Not Found.
    if not hero:
        raise HTTPException(404, "Hero not found")

    # Mark the loaded object for deletion in the current session.
    session.delete(hero)

    # Commit the transaction so the row is actually removed
    # from the database.
    session.commit()
