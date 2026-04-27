"""
06 — Dependencies: Yield Dependencies (Setup/Teardown)

This example demonstrates one of FastAPI's most important dependency patterns:
yield-based dependencies.

Covered concepts:
1. Setup before the endpoint runs
   Code before `yield` is executed before the route handler.

2. Teardown after the endpoint finishes
   Code after `yield` is executed after the response lifecycle, making it
   ideal for cleanup tasks.

3. Resource management
   This pattern is commonly used for database sessions, file handles,
   network connections, transactions, and temporary resources.

4. try/finally safety
   Cleanup code inside `finally` runs even if the endpoint raises an error.

Run:
    uvicorn examples.06_dependencies.yield_dependency:app --reload

Alternative:
    fastapi dev yield_dependency.py

Open API docs:
    http://localhost:8000/docs

Try:
    GET /data

Watch the terminal output to see:
    [DB] Connection opened
    [DB] Connection closed
"""

from typing import Annotated

from fastapi import Depends, FastAPI

# Create the FastAPI application instance.
# Its metadata appears in the generated Swagger/OpenAPI docs.
app = FastAPI(
    title="Yield Dependencies",
    description=(
        "Demonstrates setup/teardown resource handling with yield-based "
        "dependencies in FastAPI."
    ),
    version="1.0.0",
)


class FakeDatabase:
    """
    Small demonstration class simulating a database connection.

    This is not a real database client. It is only used to show the lifecycle
    of a resource that must be opened before use and closed afterward.
    """

    def __init__(self):
        print("  [DB] Connection opened")

    def query(self, sql: str):
        """
        Simulate a database query operation.

        Parameters:
        - sql: the SQL string to 'execute'

        Returns:
        - a fake query result string
        """
        return f"Result of: {sql}"

    def close(self):
        """Simulate closing the database connection."""
        print("  [DB] Connection closed")


def get_db():
    """
    Yield-based dependency that manages a database-like resource.

    Execution flow:
    1. Code before `yield` runs first (setup phase)
    2. The yielded value is injected into the endpoint
    3. After the endpoint completes, code after `yield` runs (teardown phase)

    This is the standard FastAPI pattern for managing resources that must
    always be cleaned up, such as:
    - database sessions
    - files
    - sockets
    - external service clients
    - locks / transactions

    The `finally` block ensures cleanup happens even if an exception occurs.
    """
    db = FakeDatabase()
    try:
        yield db
    finally:
        db.close()


@app.get(
    "/data",
    summary="Read data using a yield-based dependency",
    description=(
        "Uses a yield dependency to open a database-like connection before "
        "the endpoint runs and close it automatically afterward."
    ),
    tags=["Data"],
)
def read_data(db: Annotated[FakeDatabase, Depends(get_db)]):
    """
    Read data using an injected database-like resource.

    FastAPI resolves `db` by calling `get_db()`:
    - setup runs before this endpoint
    - the yielded object is passed into this function
    - teardown runs automatically after the request finishes

    Conceptually, the lifecycle is:

        db = open_resource()
        try:
            endpoint(db)
        finally:
            close_resource(db)

    This pattern is extremely important in real applications because it keeps
    resource management centralized and reliable.
    """
    return {"result": db.query("SELECT * FROM items")}