# 📘 Project 4 — TodoApp (Testing)

> **Difficulty:** ⭐⭐⭐⭐ | **Study Time:** ~1.5 hours

## 🎯 What we learn

How to write **automated tests** for FastAPI applications:

- **pytest** — Testing framework
- **TestClient** — HTTP client for endpoint testing
- **Dependency overrides** — Swap production database for a testing one
- **Fixtures** — Test data setup/teardown
- **Relative imports** — Python package structure

## 📁 Structure

```
Project 4/
└── TodoApp/
    ├── __init__.py          # ← NEW! Makes TodoApp a package
    ├── main.py
    ├── database.py
    ├── models.py
    ├── routers/
    │   ├── __init__.py      # ← NEW!
    │   ├── auth.py          # Relative imports: from ..models import Users
    │   ├── todos.py
    │   ├── admin.py
    │   └── users.py
    └── test/
        ├── __init__.py
        ├── utils.py         # Test configuration & fixtures
        ├── test_example.py  # Simple test demo
        ├── test_main.py     # Tests for main.py endpoints
        ├── test_auth.py     # Tests for authentication
        ├── test_todos.py    # Tests for CRUD operations
        ├── test_admin.py    # Tests for admin endpoints
        └── test_users.py    # Tests for user management
```

## 🚀 How to run the tests

```bash
cd "Project 4/TodoApp"

# Run ALL tests
pytest

# Run a specific file
pytest test/test_todos.py

# Verbose mode (see each test result)
pytest -v

# Show only failed tests
pytest --tb=short
```

## 📖 Code Analysis

### 1. Test Setup (`test/utils.py`)

```python
# Separate test database!
SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, ...)
TestingSessionLocal = sessionmaker(bind=engine)

# Override dependencies
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {'username': 'testuser', 'id': 1, 'user_role': 'admin'}

# Apply overrides
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

# HTTP client
client = TestClient(app)
```

> 🔑 **`dependency_overrides`** = Replaces production dependencies with test versions
> - No real DB required
> - No real JWT token required

### 2. Fixtures — Test data setup/teardown
```python
@pytest.fixture
def test_todo():
    todo = Todos(title="Learn to code!", ...)
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo                                    # Test runs here
    # CLEANUP: After the test, delete the test data
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()
```

### 3. Test Examples

```python
# ✅ Successful read
def test_read_all_authenticated(test_todo):
    response = client.get("/todo")
    assert response.status_code == 200
    assert response.json() == [{...expected data...}]

# ❌ Not found
def test_read_one_not_found():
    response = client.get("/todo/999")
    assert response.status_code == 404

# ✅ Create
def test_create_todo(test_todo):
    response = client.post('/todo/', json={...})
    assert response.status_code == 201
    # Verify in database
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == "New Todo!"

# ✅ Delete
def test_delete_todo(test_todo):
    response = client.delete('/todo/1')
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None  # Actually deleted!
```

### 4. Test Files Overview

| Test File | What it tests | Tests |
|-----------|---------------|-------|
| `test_example.py` | Simple assertions (demo) | 2 |
| `test_main.py` | `GET /`, `GET /healthy` | 2 |
| `test_auth.py` | Register, login, JWT tokens | ~4 |
| `test_todos.py` | CRUD endpoints + edge cases | 7 |
| `test_admin.py` | Admin-only endpoints | ~2 |
| `test_users.py` | Profile + password change | ~4 |

## 🔍 Key differences from Project 3

| Project 3 | Project 4 |
|-----------|-----------|
| `from models import ...` | `from ..models import ...` (relative imports) |
| No `__init__.py` | `__init__.py` inside each folder |
| Manual testing (Swagger) | Automated testing with pytest |
| Production DB only | Separate test DB |
| Real auth | Mocked auth via dependency overrides |

## ⚡ Key Takeaways

1. **Test database ≠ Production database** — Never run tests in the production DB!
2. **`dependency_overrides`** = The magic of FastAPI testing.
3. **Fixtures** = Automatic setup + cleanup of test data.
4. **Tested happy + sad paths** — Ensure you test both 200 and 400/404 responses.
5. **Relative imports** = Use `from ..models` instead of `from models` (due to package refactoring).

## ➡️ Next: [Project 5](../Project%205/) — Full-Stack app with templates!
