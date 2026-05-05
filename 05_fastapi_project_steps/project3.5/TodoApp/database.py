from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# The URL for our SQLite database file
SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'

# The engine acts as the core interface to the database.
# 'check_same_thread': False is needed only for SQLite to allow multiple threads to access it
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

# The SessionLocal will allow us to spawn specific database sessions for each request
# autocommit=False means we have to manually commit our changes to the db
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# The Base class is what all of our database models will inherit from to become SQLAlchemy tables
Base = declarative_base()
