import uuid
from datetime import datetime, timezone

from pydantic import EmailStr
from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional


# -----------------------------------------------------------------------------
# SQLModel notes
# -----------------------------------------------------------------------------
# In this file we use SQLModel classes in two different ways:
#
# 1. Database models
#    Classes declared with `table=True`, for example `class User(..., table=True)`,
#    are mapped to real database tables. Their fields become table columns and
#    their `Relationship(...)` attributes describe ORM relationships.
#
# 2. Schemas / DTOs
#    Classes without `table=True` are not database tables. They are Pydantic-style
#    schemas used for request validation and response serialization in the API.
#    Typical examples are `UserCreate`, `UserUpdate`, `UserPublic`, etc.
#
# Common naming convention used below:
# - Base   : shared fields reused by both models and schemas.
# - Create : fields accepted when creating a resource through the API.
# - Update : fields accepted when updating a resource through the API.
# - Public : fields returned to the client through the API.
# - PluralPublic : wrapper schema for list responses, usually with data + count.
# -----------------------------------------------------------------------------


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


# -----------------------------------------------------------------------------
# User schemas and model
# -----------------------------------------------------------------------------


# Base schema: shared user fields used by API schemas and the DB model.
# This is not a DB table because it does not use `table=True`.
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# API schema: data received when an admin/system creates a user.
# It extends UserBase and adds the plain password received from the client.
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


# API schema: data received when a user registers.
# It is separated from UserCreate so registration can expose only the fields
# that a normal user is allowed to submit.
class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# API schema: data received when updating a user.
# All fields are optional because PATCH/partial-update endpoints should allow
# the client to send only the fields that need to change.
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore[assignment]
    password: str | None = Field(default=None, min_length=8, max_length=128)


# API schema: fields a logged-in user can update for their own account.
class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


# API schema: payload used for changing an existing password.
class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model: this class maps to the `user` table because of `table=True`.
# It contains database-only fields such as `id`, `hashed_password`, timestamps,
# and ORM relationships. Notice that we store `hashed_password`, not the plain
# password received by UserCreate/UserRegister
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    # ORM relationships: these are not plain API fields.
    # They connect this user with the related rows in other tables.
    # `cascade_delete=True` means related records are deleted when the user is deleted.
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    todos: list["Todo"] = Relationship(back_populates="owner", cascade_delete=True)
    search_sessions: list["SearchSession"] = Relationship(
        back_populates="owner", cascade_delete=True
    )


# API response schema: public representation of a user.
# It intentionally excludes sensitive/internal fields such as `hashed_password`.
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None


# API response schema: standard list response for users.
class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# -----------------------------------------------------------------------------
# Item schemas and model
# -----------------------------------------------------------------------------


# Base schema: fields common to items in create/update/public contexts.
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# API schema: payload for creating an item.
class ItemCreate(ItemBase):
    pass


# API schema: payload for updating an item.
# `title` becomes optional so clients can update only part of the item.
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore[assignment]


# Database model: maps to the `item` table.
# Contains DB-specific fields such as primary key, timestamp, foreign key,
# and relationship back to the owning user.
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# API response schema: public item returned to clients.
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


# API response schema: standard list response for items.
class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# -----------------------------------------------------------------------------
# Authentication and generic API schemas
# -----------------------------------------------------------------------------


# Generic API response schema for simple messages.
class Message(SQLModel):
    message: str


# API response schema: JSON payload returned after successful authentication.
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Internal/API schema: decoded JWT token contents.
# `sub` usually stores the subject/user identifier.
class TokenPayload(SQLModel):
    sub: str | None = None


# API schema: payload used when resetting a password with a token.
class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


# -----------------------------------------------------------------------------
# Todo schemas and model
# -----------------------------------------------------------------------------


# Base schema: shared Todo fields.
# This is reused by TodoCreate, TodoPublic, and the Todo DB model.
class TodoBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    completed: bool = Field(default=False)


# Database model: maps to the `todo` table.
# Includes persistence-related fields that should not be required from the client,
# such as `id`, `created_at`, and `owner_id`.
class Todo(TodoBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    # Foreign key column: links each Todo row to one User row.
    # ondelete="CASCADE" asks the database to delete todos when the owner is deleted.
    owner_id: uuid.UUID = Field(
        foreign_key="user.id",
        nullable=False,
        ondelete="CASCADE",
    )
    # ORM relationship: lets Python code access todo.owner instead of manually
    # querying the user table by owner_id.
    owner: User | None = Relationship(back_populates="todos")


# API schema: payload for creating a todo.
class TodoCreate(TodoBase):
    pass


# API schema: payload for updating a todo.
# Every field is optional to support partial updates.
class TodoUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore[assignment]
    description: str | None = Field(default=None, max_length=255)  # type: ignore[assignment]
    completed: bool | None = Field(default=None)  # type: ignore[assignment]


# API response schema: public todo returned to the client.
class TodoPublic(TodoBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


# API response schema: standard list response for todos.
class TodosPublic(SQLModel):
    data: list[TodoPublic]
    count: int


# -----------------------------------------------------------------------------
# Searching agent session schemas and model
# -----------------------------------------------------------------------------


# Base schema: common fields for a search session.
class SearchSessionBase(SQLModel):
    title: str = Field(default="Untitles Search", max_length=255)


# Database model: maps to the `search_session` table.
# Represents one conversation/session of the searching agent for a specific user.
class SearchSession(SearchSessionBase, table=True):
    __tablename__ = "search_session"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    # Stored as JSON text, for example:
    # [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    # It keeps the conversational memory/context for this search session.
    memory: str = Field(default="[]")

    # Timestamps for session lifecycle.
    # Note: datetime.utcnow() returns a naive datetime. If you want timezone-aware
    # timestamps everywhere, prefer get_datetime_utc consistently.
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # ORM relationships.
    # owner: the User that owns the session.
    # history: all SearchHistory rows belonging to this session.
    owner: User = Relationship(back_populates="search_sessions")
    history: List["SearchHistory"] = Relationship(
        back_populates="session", cascade_delete=True
    )


# API schema: payload for creating a new search session.
class SearchSessionCreate(SearchSessionBase):
    pass


# API schema: payload for updating a search session.
# Only title is editable here, and it is optional for partial update endpoints.
class SearchSessionUpdate(SQLModel):
    title: Optional[str] = Field(default=None, max_length=255)


# API response schema: public search session returned to the client.
class SearchSessionPublic(SearchSessionBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# API response schema: standard list response for search sessions.
class SearchSessionsPublic(SQLModel):
    data: list[SearchSessionPublic]
    count: int


# -----------------------------------------------------------------------------
# Search history schemas and model
# -----------------------------------------------------------------------------


# Base schema: shared fields for a single search/answer entry.
class SearchHistoryBase(SQLModel):
    query: str
    result: Optional[str] = (
        None  # Agent answer. None means no result has been stored yet.
    )


# Database model: maps to the `search_history` table.
# Represents one user query and the corresponding agent result inside a session.
class SearchHistory(SearchHistoryBase, table=True):
    __tablename__ = "search_history"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Foreign key to the session where this query belongs.
    session_id: uuid.UUID = Field(
        foreign_key="search_session.id", nullable=False, ondelete="CASCADE"
    )
    # Foreign key to the user who made the query.
    # Keeping owner_id here makes it easier to filter a user's history directly.
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # ORM relationships for navigation in Python code.
    session: SearchSession = Relationship(back_populates="history")
    owner: User = Relationship()


# API schema: payload for creating a search history entry.
# The client/API layer must specify which session the query belongs to.
class SearchHistoryCreate(SearchHistoryBase):
    session_id: uuid.UUID


# API response schema: public search history entry returned to the client.
class SearchHistoryPublic(SearchHistoryBase):
    id: uuid.UUID
    session_id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime


# API response schema: standard list response for search history entries.
class SearchHistoriesPublic(SQLModel):
    data: list[SearchHistoryPublic]
    count: int


# -----------------------------------------------------------------------------
# Agent chat API schemas
# -----------------------------------------------------------------------------


# API request schema: message sent by the client to the agentic chat endpoint.
class AgentChatRequest(SQLModel):
    message: str


# API response schema: answer returned by the agentic chat endpoint.
class AgentChatResponse(SQLModel):
    session_id: uuid.UUID
    reply: str
