# 📘 Project 3 — TodoApp (Database & Authentication)

> **Difficulty:** ⭐⭐⭐ | **Study Time:** ~1.5 hours

## 🎯 What we learn

A major leap! From in-memory lists we move to a **real database** + **JWT authentication**:

- **SQLAlchemy** — ORM for database operations
- **JWT tokens** — Authentication (login → token → protected routes)
- **Password hashing** — bcrypt (never store plaintext passwords!)
- **APIRouter** — Organizing code across multiple files
- **Dependency Injection** — `Depends()` for auth & database sessions

## 📁 Structure

```
Project 3/
└── TodoApp/
    ├── main.py              # FastAPI app + router connections
    ├── database.py          # SQLAlchemy engine & session setup
    ├── models.py            # Database models (Users, Todos)
    └── routers/
        ├── __init__.py
        ├── auth.py          # Login, register, JWT tokens
        ├── todos.py         # CRUD for todos (protected!)
        ├── admin.py         # Admin endpoints
        └── users.py         # User profile management
```

## 🚀 How to run it

```bash
cd "Project 3/TodoApp"
uvicorn main:app --reload
```

## 📖 Code Analysis

### 1. Database Setup (`database.py`)
```python
engine = create_engine("sqlite:///./todosapp.db")
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
```
> Uses **SQLite** — a `.db` file in the local filesystem. No server installation required!

### 2. Models (`models.py`) — Database Tables

| Model | Fields | Relationship |
|-------|--------|--------------|
| `Users` | id, email, username, first_name, last_name, hashed_password, is_active, role, phone_number | 1-to-Many |
| `Todos` | id, title, description, priority, complete, owner_id (FK) | belongs_to User |

### 3. Authentication (`routers/auth.py`)

**Registration flow:**
```
POST /auth → username, password → hash(password) → save to DB → 201 Created
```

**Login flow:**
```
POST /auth/token → username, password → verify hash →
    ✅ match → create JWT token → return token
    ❌ no match → 401 Unauthorized
```

**Key functions:**
| Function | Purpose |
|----------|---------|
| `bcrypt_context.hash(password)` | Hash password before storing |
| `bcrypt_context.verify(plain, hash)` | Compare password during login |
| `create_access_token(username, id, role, expires)` | Generate JWT |
| `get_current_user(token)` | Decode JWT → return user info |

### 4. Protected Endpoints (`routers/todos.py`)

```python
# Dependency injection chain:
db_dependency = Annotated[Session, Depends(get_db)]        # Database session
user_dependency = Annotated[dict, Depends(get_current_user)]  # Authenticated user

@router.get("/")
async def read_all(user: user_dependency, db: db_dependency):
    # user = authenticated user info (from JWT)
    # db = database session
    return db.query(Todos).filter(Todos.owner_id == user["id"]).all()
```

> 🔑 **Each user only sees their own todos!**

### 5. Endpoints Overview

| Router | Method | Endpoint | Auth? | Purpose |
|--------|--------|----------|-------|---------|
| `auth` | POST | `/auth` | ❌ | Register |
| `auth` | POST | `/auth/token` | ❌ | Login → JWT |
| `todos` | GET | `/todos` | ✅ | List todos |
| `todos` | GET | `/todos/todo/{id}` | ✅ | Single todo |
| `todos` | POST | `/todos/todo` | ✅ | Create |
| `todos` | PUT | `/todos/todo/{id}` | ✅ | Update |
| `todos` | DELETE | `/todos/todo/{id}` | ✅ | Delete |
| `admin` | GET | `/admin/todo` | ✅ 🔒 | All todos (admin only) |
| `admin` | DELETE | `/admin/todo/{id}` | ✅ 🔒 | Delete (admin only) |
| `users` | GET | `/user` | ✅ | Profile |
| `users` | PUT | `/user/password` | ✅ | Change password |
| `users` | PUT | `/user/phonenumber/{phone}` | ✅ | Update phone |

## 🔍 New concepts compared to Project 2

| Project 2 | Project 3 |
|-----------|-----------|
| In-memory list | SQLAlchemy + SQLite |
| Single file | Multiple files + routers |
| No auth | JWT + bcrypt |
| No Depends | `Depends(get_db)`, `Depends(get_current_user)` |
| Data lost on restart | Persistent database |

## ⚡ Key Takeaways

1. **APIRouter** = Code separation → `auth.py`, `todos.py`, `admin.py`, `users.py`
2. **`Depends()`** = Dependency Injection → Database sessions + Auth validation
3. **JWT tokens** = Stateless authentication (no server-side sessions required)
4. **NEVER plaintext passwords** — Always `bcrypt.hash()` before storing
5. **Owner filtering** — `filter(Todos.owner_id == user["id"])` → data isolation

## ➡️ Next: [Project 3.5](../Project%203.5/) — Alembic migrations!
