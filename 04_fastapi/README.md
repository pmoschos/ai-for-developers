# FastAPI — The Complete Guide & Tutorial

---

## 🎯 Purpose

This repository transforms a comprehensive FastAPI course into an organized, hands-on learning experience. It covers everything from a 7-line Hello World to a fully structured, authenticated, tested, and deployable Python API.

## ✅ Prerequisites

| Requirement | Details |
|-------------|---------|
| **Python 3.11+** | Check with `python --version` |
| **pip or uv** | Any Python package manager |
| **Code editor** | VS Code or PyCharm recommended |
| **Basic Python** | Functions, classes, decorators, imports, type hints |
| **HTTP basics** | Request/response, GET/POST/PUT/DELETE, status codes |

---

## 📁 Repository Structure

```
FastAPI-Tut-Me/
├── docs/           → Theory & concept notes (14 topics)
├── examples/       → Isolated, runnable examples by topic (beginner → intermediate)
├── app/            → Organized multi-file FastAPI application (intermediate → advanced)
├── tests/          → Test suite for the organized app
├── README.md
├── requirements.txt
├── .env.example
├── Dockerfile
└── .dockerignore
```

### Three Learning Layers

| Layer | What | Complexity |
|-------|------|------------|
| `examples/` | One concept at a time, self-contained scripts | ⭐ Beginner |
| `app/` | Production-style multi-file project | ⭐⭐ Intermediate |
| `tests/` | Testing the organized app with pytest | ⭐⭐⭐ Advanced |

---

## 🚀 Installation

```bash
# 1. Clone or navigate to the repository
cd project-name-folder

# 2. Create a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3. Install all dependencies
pip install -r requirements.txt

# 4. Copy the environment file
copy .env.example .env        # Windows
cp .env.example .env          # macOS / Linux
```

---

## ▶️ How to Run

### Run a Simple Example

Each example is a standalone script. Run any of them with:

```bash
# From the repository root
uvicorn examples.01_getting_started.main:app --reload

# Then open http://127.0.0.1:8000/docs in your browser
```

### Run the Organized Application

```bash
uvicorn app.main:app --reload

# Interactive docs:  http://127.0.0.1:8000/docs
# ReDoc:             http://127.0.0.1:8000/redoc
```

### Run the Test Suite

```bash
pytest tests/ -v
```

---

## 📖 Recommended Study Order

Follow this sequence. For each topic, read the `docs/` note first, then study the `examples/` code.

| Step | Topic | Read | Code |
|------|-------|------|------|
| 1 | Getting Started | `docs/01_getting_started.md` | `examples/01_getting_started/` |
| 2 | Path & Query Parameters | `docs/02_parameters.md` | `examples/02_parameters/` |
| 3 | Request Bodies | `docs/03_request_bodies.md` | `examples/03_request_bodies/` |
| 4 | Responses | `docs/04_responses.md` | `examples/04_responses/` |
| 5 | Error Handling | `docs/05_errors.md` | `examples/05_errors/` |
| 6 | Dependency Injection | `docs/06_dependencies.md` | `examples/06_dependencies/` |
| 7 | Async & Concurrency | `docs/07_async.md` | `examples/07_async/` |
| 8 | Database with SQLModel | `docs/08_database.md` | `examples/08_database/` |
| 9 | Authentication with JWT | `docs/09_authentication.md` | `examples/09_auth/` |
| 10 | Project Structure | `docs/10_project_structure.md` | `app/` (the full project) |
| 11 | Middleware & CORS | `docs/11_middleware_and_cors.md` | `examples/11_middleware/` |
| 12 | Testing | `docs/12_testing.md` | `tests/` |
| 13 | Advanced Features | `docs/13_advanced.md` | `examples/13_advanced/` |
| 14 | Deployment | `docs/14_deployment.md` | `Dockerfile` |

---

## 🎓 Learning Outcomes

After completing this guide, you will be able to:

- Build REST APIs with FastAPI using Python type hints
- Validate request data with Pydantic models and custom validators
- Handle errors with HTTPException and custom exception handlers
- Use dependency injection for shared logic, auth, and DB sessions
- Choose between sync and async endpoints appropriately
- Integrate a SQLite database using SQLModel (Pydantic + SQLAlchemy)
- Implement JWT-based authentication with OAuth2 password flow
- Organize a multi-file FastAPI project with routers, models, and config
- Add CORS, custom middleware, and lifespan events
- Write API tests with TestClient, pytest, and dependency overrides
- Handle file uploads, serve static files, render templates, and use WebSockets
- Deploy with Uvicorn, Gunicorn, and Docker

---

## 🐳 Deployment Overview

```bash
# Build the Docker image
docker build -t fastapi-tutorial .

# Run the container
docker run -d -p 8000:8000 fastapi-tutorial
```

For production, see `docs/14_deployment.md` for:
- Uvicorn worker tuning
- Gunicorn + Uvicorn workers
- Production checklist (HTTPS, CORS, secrets, Alembic, observability)

---

## 📚 Resources

| Resource | URL |
|----------|-----|
| FastAPI Official Docs | [fastapi.tiangolo.com](https://fastapi.tiangolo.com) |
| SQLModel Docs | [sqlmodel.tiangolo.com](https://sqlmodel.tiangolo.com) |
| Pydantic Docs | [docs.pydantic.dev](https://docs.pydantic.dev) |
| Starlette (ASGI) | [starlette.io](https://www.starlette.io) |

---

## 📝 Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.11+ | Language |
| FastAPI | Web framework |
| Pydantic | Data validation |
| SQLModel | ORM (Pydantic + SQLAlchemy) |
| SQLite | Database |
| Uvicorn | ASGI server |
| passlib + bcrypt | Password hashing |
| python-jose | JWT tokens |
| pydantic-settings | Environment configuration |
| pytest + httpx | Testing |
| Jinja2 | HTML templates |
| Docker | Containerization |

---

## 📢 Stay Updated

Be sure to ⭐ this repository to stay updated with new examples and enhancements!

## 📄 License
🔐 This project is protected under the [MIT License](https://mit-license.org/).


## Contact 📧
Panagiotis Moschos - pan.moschos86@gmail.com

🔗 *Note: This is a Python script and requires a Python interpreter to run.*

---

<h1 align=center>Happy Coding 👨‍💻 </h1>

<p align="center">
  Made with ❤️ by 
  <a href="https://www.linkedin.com/in/panagiotis-moschos" target="_blank">
  Panagiotis Moschos</a>
</p>