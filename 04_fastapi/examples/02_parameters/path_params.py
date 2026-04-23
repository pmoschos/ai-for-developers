"""
02 — Path Parameters: Basics

This example introduces two common FastAPI path parameter patterns:

1. Standard typed path parameters
   Example:
       /users/42
   FastAPI validates and converts the value based on the Python type hint.

2. Catch-all path parameters using :path
   Example:
       /files/home/user/data.csv
   FastAPI captures the whole remaining URL path, including slashes.

Run:
    uvicorn examples.02_parameters.path_params:app --reload

Alternative:
    fastapi dev path_params.py

Open API docs:
    http://localhost:8000/docs

Try:
    GET /users/42
        -> {"user_id": 42, "kind": "int"}

    GET /users/abc
        -> 422 Unprocessable Entity

    GET /files/report.txt
        -> {"file_path": "report.txt"}

    GET /files/home/user/data.csv
        -> {"file_path": "home/user/data.csv"}
"""


# To run this code:
# fastapi dev path_params.py
# or
# uvicorn path_params:app --reload
# To view the Swagger UI documentation:
# http://localhost:8000/docs

from fastapi import FastAPI

# Create the FastAPI application instance.
# The title appears in the generated Swagger/OpenAPI docs.
app = FastAPI(
    title="Path Parameters",
    description=(
        "Demonstrates how to validate and handle path parameters. "
        "Includes standard integer parameters and catch-all :path parameters."
    ),
    version="1.0.0",
)


@app.get("/users/{user_id}",
    summary="Get a user by numeric ID",
    description=(
        "Accepts a user ID as a path parameter. "
        "FastAPI validates that the value is an integer, converts it "
        "automatically, and returns a 422 error if conversion fails."
    ),
    tags=["Users"])
def get_user(user_id: int):
    """
    Return a user identifier received from the URL path.

    The type hint `int` is important because FastAPI uses it to:
    1. validate that the incoming value is a valid integer,
    2. convert the path value from string to int automatically,
    3. reject invalid values before entering the function.

    Example:
        /users/42    -> valid
        /users/abc   -> invalid, returns 422
    """
    return {
      "user_id": user_id, # returns the integer user id
      "kind": type(user_id).__name__ # shows that the value is really an int
    }


@app.get("/files/{file_path:path}",
    summary="Read a file path from the URL",
    description=(
        "Uses FastAPI's special `:path` converter to capture the entire "
        "remaining path, including slashes."
    ),
    tags=["Files"])
def read_file(file_path: str):
    """
    Return the full file path captured from the URL.

    Normally, a path parameter stops at the next `/`.
    By using `{file_path:path}`, FastAPI captures the rest of the URL
    as a single value.

    Example:
        /files/report.txt
            -> file_path = 'report.txt'

        /files/home/user/data.csv
            -> file_path = 'home/user/data.csv'
    """
    return {"file_path": file_path}
