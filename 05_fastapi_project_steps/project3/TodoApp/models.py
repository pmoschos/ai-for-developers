from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


# The Users class inherits from Base, turning it into a database model
class Users(Base):
    # __tablename__ defines the actual name of the table in the database
    __tablename__ = 'users'

    # Defining the columns for the users table
    id = Column(Integer, primary_key=True, index=True) # index=True makes queries faster
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True) # Users are active by default
    role = Column(String)


class Todos(Base):
    __tablename__ = 'todos'

    # Defining the columns for the todos table
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    # The ForeignKey links this todo directly to a specific user's ID
    owner_id = Column(Integer, ForeignKey("users.id"))
