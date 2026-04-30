# 12 — Testing

Self-contained testing examples you can study and run directly.

Each file contains **both** a small FastAPI app and its tests,
so you can see everything in one place without jumping between files.

## Files

| File | What It Teaches |
|------|-----------------|
| `test_01_basics.py` | TestClient basics, assertions, query params, error responses |
| `test_02_database.py` | Dependency override, in-memory SQLite + StaticPool, CRUD tests, test isolation |
| `test_03_auth.py` | Auth testing: registration, login, JWT tokens, protected routes, admin vs. user |

## How to Run

```bash
# Run all examples
pytest examples/12_testing/ -v

# Run a single file
pytest examples/12_testing/test_01_basics.py -v

# Run a specific test
pytest examples/12_testing/test_01_basics.py::test_create_item -v
```

## Key Concepts Demonstrated

### 1. TestClient (test_01)
```python
from fastapi.testclient import TestClient
client = TestClient(app)

response = client.get("/")
assert response.status_code == 200
```

### 2. Dependency Override + In-Memory DB (test_02)
```python
test_engine = create_engine("sqlite://", poolclass=StaticPool)

def override_get_session():
    with Session(test_engine) as session:
        yield session

app.dependency_overrides[get_session] = override_get_session
```

### 3. Testing Auth Endpoints (test_03)
```python
# Login to get a token
response = client.post("/login", data={"username": "u", "password": "p"})
token = response.json()["access_token"]

# Use the token in protected requests
client.get("/me", headers={"Authorization": f"Bearer {token}"})
```

See `docs/12_testing.md` for the theory.


### 4. Run all the tests

```bash
pytest . -v

```

or

```bash
pytest test_01_basics.py test_02_database.py test_03_auth.py -v
```