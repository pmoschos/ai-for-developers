# 09 — Authentication with JWT

Learn how to secure your API with password hashing, JSON Web Tokens, and protected endpoints.

## What You Will Learn

- The OAuth2 password flow: credentials in → token out → token on every request
- How to hash passwords securely with bcrypt
- How to create and verify JWT tokens
- How to build a login endpoint and a `get_current_user` dependency
- How to protect endpoints with authentication and role-based access

## Files

| File | What It Teaches |
|------|-----------------|
| `password_hashing.py` | Standalone demo of `passlib` + bcrypt (run as a script) |
| `jwt_demo.py` | Standalone demo of creating + decoding JWT tokens (run as a script) |
| `main.py` | Full auth app: register, login, `/me`, `/admin` |

### Enhanced Implementation

The `enhanced_implementations/main.py` contains the same app with detailed docstrings and comments for every function.

## How to Run

```bash
# Standalone demos (run as scripts, no server needed)
python password_hashing.py
python jwt_demo.py

# Full auth app (from this directory)
uvicorn main:app --reload
```

Then visit http://127.0.0.1:8000/docs and follow this flow:

1. **POST /register** → create a user (use `admin` as username for admin rights)
2. **POST /login** → get an access token
3. **Click "Authorize"** in Swagger UI → paste the token
4. **GET /me** → see your user info (requires auth)
5. **GET /admin** → admin-only endpoint (requires admin role)

## Key Concepts

### The Auth Flow
```
Client                          Server
  │                               │
  ├── POST /login (user+pass) ──→ │ verify password
  │                               │ create JWT
  ←── {"access_token": "..."}  ───┤
  │                               │
  ├── GET /me                  ──→ │ decode JWT
  │   Authorization: Bearer xxx   │ look up user
  ←── {"username": "alice"}    ───┤
```

### Password Hashing
Never store plaintext passwords:
```python
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash("my-password")
pwd_context.verify("guess", hashed)  # True / False
```

### JWT Tokens
```python
token = jwt.encode({"sub": username, "exp": expiry}, SECRET_KEY, algorithm="HS256")
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
```

### Protecting Endpoints
```python
CurrentUser = Annotated[User, Depends(get_current_user)]

@app.get("/me")
def me(user: CurrentUser):
    return user
```

See `docs/09_authentication.md` for the full theory.
