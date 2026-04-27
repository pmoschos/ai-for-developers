"""
06 — Dependencies: Class-Based Dependency

This example demonstrates how FastAPI can use a class as a dependency
instead of a regular function.

Covered concepts:
1. Class-based dependencies
   FastAPI can instantiate a class and inject the created object
   into an endpoint.

2. Constructor parameters as request parameters
   The class __init__ parameters are treated like dependency parameters,
   so FastAPI reads and validates them from the request.

3. Typed injected objects
   A class dependency gives you named attributes such as `p.skip`
   and `p.limit` instead of working with a plain dictionary.

4. Depends() without an explicit callable
   When the type hint and the dependency match, `Depends()` can infer
   the dependency from the annotated type.

Run:
    uvicorn examples.06_dependencies.class_dependency:app --reload

Alternative:
    fastapi dev class_dependency.py

Open API docs:
    http://localhost:8000/docs

Try:
    GET /items?skip=5&limit=3
"""

from typing import Annotated

from fastapi import Depends, FastAPI, Query

# Create the FastAPI application instance.
# Its metadata appears in the generated Swagger/OpenAPI docs.
app = FastAPI(
    title="Class Dependencies",
    description=(
        "Demonstrates how to use a class as a FastAPI dependency so that "
        "query parameters are injected into an instantiated object."
    ),
    version="1.0.0",
)

# Fake in-memory data used only for demonstration.
fake_items = [{"name": f"Item {i}"} for i in range(100)]


class Pager:
    """
    Class-based dependency representing pagination parameters.

    FastAPI will instantiate this class automatically when it is used
    as a dependency. Its constructor parameters become request parameters.

    Benefits of using a class dependency:
    - clearer attribute access (`p.skip` instead of `page["skip"]`)
    - stronger structure than a plain dictionary
    - convenient grouping of related parameters
    """

    def __init__(
        self,
        skip: Annotated[
            int,
            Query(
                description="Number of records to skip",
                examples=[5],
                ge=0,
            ),
        ] = 0,
        limit: Annotated[
            int,
            Query(
                description="Maximum number of records to return",
                examples=[3],
                ge=1,
                le=100,
            ),
        ] = 10,
    ):
        """
        Initialize the pager from query parameters.

        FastAPI treats these constructor arguments similarly to endpoint
        parameters:
        - reads them from the request
        - validates them
        - converts them to the expected Python types
        """
        self.skip = skip
        self.limit = limit


@app.get(
    "/items",
    summary="List items using a class-based pagination dependency",
    description=(
        "Uses the Pager class as a dependency. FastAPI creates a Pager "
        "instance from query parameters and injects it into the endpoint."
    ),
    tags=["Items"],
)
def list_items(p: Annotated[Pager, Depends()]):
    """
    Return a paginated slice of fake items.

    `Depends()` with no explicit argument means:
    use the annotated type (`Pager`) itself as the dependency.

    So for a request like:
        /items?skip=5&limit=3

    FastAPI effectively does something conceptually similar to:
        p = Pager(skip=5, limit=3)

    and then injects that instance into this function.

    This is useful when you want:
    - reusable grouped parameters
    - attribute access instead of dictionary lookups
    - cleaner modeling of dependency state
    """
    return {
        "skip": p.skip,
        "limit": p.limit,
        "count": len(fake_items[p.skip: p.skip + p.limit]),
        "items": fake_items[p.skip: p.skip + p.limit],
    }