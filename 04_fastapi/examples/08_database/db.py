"""
08 — Database: Engine, Session & create_all

Core idea:
- one engine per application process
- one session per request / unit of work

The engine is long-lived.
The session is short-lived.
"""

from sqlmodel import Session, SQLModel, create_engine

# SQLite database file stored in the current project directory.
# Example:
#   sqlite:///./database.db
# means "use a local SQLite file named database.db"
DATABASE_URL = "sqlite:///./database.db"

# The engine is the central object that knows how to talk to the database.
# It manages:
# - database connections
# - connection reuse / pooling
# - low-level communication with the DB
#
# In most applications, the engine is created once and reused.
engine = create_engine(
    DATABASE_URL,
    # echo=False -> SQL queries are not printed in the terminal
    # echo=True  -> useful during development/debugging to see generated SQL
    echo=False,
    # SQLite has a threading limitation by default.
    # check_same_thread=False allows the same database connection setup
    # to be used in contexts like FastAPI, where requests may involve
    # different threads.
    #
    # This is commonly required when using SQLite with web applications.
    connect_args={"check_same_thread": False},  # required for SQLite
)


def create_db_and_tables():
    """
    Create all database tables registered in SQLModel metadata.

    SQLModel collects all classes that use table=True and stores their
    table definitions in metadata.

    create_all(engine):
    - creates missing tables
    - does NOT delete existing tables
    - does NOT automatically apply schema migrations

    Important:
    If you later change a model (for example add/remove a column),
    create_all() is usually not enough for production systems.
    In that case, a migration tool such as Alembic is preferred.
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Provide a database session, typically one per request.

    A Session represents a working conversation with the database.
    It is used to:
    - add objects
    - query data
    - update rows
    - delete rows
    - commit or roll back transactions

    Using `with Session(engine) as session` ensures:
    - the session is opened when needed
    - the session is automatically closed afterwards

    `yield session` makes this function suitable as a dependency in frameworks such as FastAPI.
    """
    with Session(engine) as session:
        yield session
