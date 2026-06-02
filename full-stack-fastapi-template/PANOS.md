# 📘 Αναλυτικός Οδηγός Project

## Full Stack FastAPI Template

> **Σκοπός:** Αναλυτικός οδηγός που εξηγεί τη δομή και τη λειτουργία **κάθε αρχείου** του project.

---

## 📋 Πίνακας Περιεχομένων

- [Επισκόπηση Project](#-επισκόπηση-project)
- [Δομή Φακέλων (Tree)](#-δομή-φακέλων-tree)
- [Root-Level Αρχεία](#-root-level-αρχεία)
- [Φάκελος `.copier/`](#-φάκελος-copier)
- [Φάκελος `.github/`](#-φάκελος-github)
- [Φάκελος `.vscode/`](#-φάκελος-vscode)
- [Φάκελος `hooks/`](#-φάκελος-hooks)
- [Φάκελος `img/`](#-φάκελος-img)
- [Φάκελος `scripts/`](#-φάκελος-scripts-root)
- [Φάκελος `backend/`](#-φάκελος-backend)
  - [Backend Root Αρχεία](#backend-root-αρχεία)
  - [Backend `app/` — Κύριος κώδικας](#backend-app--κύριος-κώδικας)
  - [Backend `app/core/`](#backend-appcore)
  - [Backend `app/api/`](#backend-appapi)
  - [Backend `app/api/routes/`](#backend-appapiroutes)
  - [Backend `app/agent/`](#backend-appagent)
  - [Backend `app/alembic/`](#backend-appalembic)
  - [Backend `app/email-templates/`](#backend-appemail-templates)
  - [Backend `scripts/`](#backend-scripts)
  - [Backend `tests/`](#backend-tests)
- [Φάκελος `frontend/`](#-φάκελος-frontend)
  - [Frontend Root Αρχεία](#frontend-root-αρχεία)
  - [Frontend `src/`](#frontend-src)
  - [Frontend `src/client/`](#frontend-srcclient)
  - [Frontend `src/components/`](#frontend-srccomponents)
  - [Frontend `src/hooks/`](#frontend-srchooks)
  - [Frontend `src/lib/`](#frontend-srclib)
  - [Frontend `src/routes/`](#frontend-srcroutes)
  - [Frontend `tests/`](#frontend-tests)

---

## 🏗 Επισκόπηση Project

Αυτό το project είναι ένα **Full-Stack Web Application** που αποτελείται από:

| Layer | Τεχνολογία | Περιγραφή |
|-------|-----------|-----------|
| **Backend** | FastAPI + Python | REST API, authentication, CRUD, AI Agent |
| **Frontend** | React + TypeScript + Vite | SPA dashboard με TanStack Router & shadcn/ui |
| **Database** | PostgreSQL | Κύρια βάση δεδομένων, migrations μέσω Alembic |
| **AI Agent** | LangChain + OpenAI + Tavily | Αgent για web search |
| **Gradio UI** | Gradio | Εναλλακτικό chat interface για τον AI agent |
| **Containerization** | Docker + Docker Compose | Deployment σε containers |
| **Reverse Proxy** | Traefik | Routing & TLS σε production |
| **CI/CD** | GitHub Actions | Αυτοματοποιημένα tests & deployments |

---

## 🌳 Δομή Φακέλων (Tree)

```
full-stack-fastapi-template/
├── .copier/                          # Copier template engine config
├── .env                              # Κεντρικές env μεταβλητές
├── .git/                             # Git repository
├── .gitattributes                    # Git line-ending κανόνες
├── .github/                          # GitHub Actions & config
│   ├── dependabot.yml
│   ├── labeler.yml
│   └── workflows/                    # 14 CI/CD workflows
├── .gitignore                        # Root git ignore
├── .pre-commit-config.yaml           # Pre-commit hooks
├── .vscode/                          # VS Code config
├── CONTRIBUTING.md                   # Οδηγίες contribution
├── LICENSE                           # MIT License
├── README.md                         # Κύριο README
├── backend/                          # FastAPI Backend
│   ├── .dockerignore
│   ├── .gitignore
│   ├── Dockerfile
│   ├── README.md
│   ├── alembic.ini
│   ├── gradio_app.py                 # Gradio Chat UI
│   ├── pyproject.toml
│   ├── app/                          # Κύριος κώδικας εφαρμογής
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI app entry point
│   │   ├── models.py                 # SQLModel models & Pydantic schemas
│   │   ├── crud.py                   # CRUD operations
│   │   ├── utils.py                  # Email & token utilities
│   │   ├── backend_pre_start.py      # DB readiness check
│   │   ├── initial_data.py           # Seed initial data
│   │   ├── tests_pre_start.py        # Pre-test DB check
│   │   ├── core/                     # Core configuration
│   │   │   ├── __init__.py
│   │   │   ├── config.py             # Settings (Pydantic)
│   │   │   ├── db.py                 # SQLAlchemy engine & init
│   │   │   └── security.py           # JWT & password hashing
│   │   ├── api/                      # API layer
│   │   │   ├── __init__.py
│   │   │   ├── main.py               # Router aggregation
│   │   │   ├── deps.py               # Dependencies (auth, DB session)
│   │   │   └── routes/               # API endpoints
│   │   │       ├── __init__.py
│   │   │       ├── login.py
│   │   │       ├── users.py
│   │   │       ├── items.py
│   │   │       ├── todos.py
│   │   │       ├── searches.py
│   │   │       ├── private.py
│   │   │       └── utils.py
│   │   ├── agent/                    # AI Search Agent
│   │   │   ├── graph.py              # Agent graph & execution
│   │   │   └── tools.py              # Tavily web search tool
│   │   ├── alembic/                  # DB migrations
│   │   │   ├── README
│   │   │   ├── env.py
│   │   │   ├── script.py.mako
│   │   │   └── versions/             # Migration scripts
│   │   └── email-templates/          # Email HTML templates
│   │       ├── src/                  # MJML sources
│   │       └── build/                # Compiled HTML
│   ├── scripts/                      # Bash scripts
│   └── tests/                        # Backend test suite
├── frontend/                         # React Frontend
│   ├── .dockerignore
│   ├── .env
│   ├── .gitignore
│   ├── Dockerfile
│   ├── Dockerfile.playwright
│   ├── README.md
│   ├── biome.json
│   ├── components.json
│   ├── index.html
│   ├── nginx.conf
│   ├── nginx-backend-not-found.conf
│   ├── openapi-ts.config.ts
│   ├── package.json
│   ├── playwright.config.ts
│   ├── tsconfig.json
│   ├── tsconfig.build.json
│   ├── tsconfig.node.json
│   ├── vite.config.ts
│   ├── public/                       # Static assets
│   ├── src/                          # Source code
│   │   ├── main.tsx                  # React entry point
│   │   ├── index.css                 # Global styles
│   │   ├── utils.ts                  # Error handling utilities
│   │   ├── vite-env.d.ts             # Vite type definitions
│   │   ├── routeTree.gen.ts          # Auto-generated route tree
│   │   ├── client/                   # Auto-generated API client
│   │   ├── components/               # React components
│   │   ├── hooks/                    # Custom React hooks
│   │   ├── lib/                      # Library utilities
│   │   └── routes/                   # File-based routes
│   └── tests/                        # Playwright E2E tests
├── hooks/                            # Copier hooks
├── img/                              # Documentation images
├── scripts/                          # Root-level scripts
├── compose.yml                       # Docker Compose (production)
├── compose.override.yml              # Docker Compose (local dev)
├── compose.traefik.yml               # Traefik configuration
├── copier.yml                        # Copier template config
├── package.json                      # Root workspace (bun)
├── pyproject.toml                    # Root workspace (uv)
├── bun.lock                          # Bun lockfile
├── uv.lock                           # UV lockfile
├── deployment.md                     # Deployment guide
├── development.md                    # Development guide
└── release-notes.md                  # Changelog
```

---

## 📁 Root-Level Αρχεία

### `.env`
**Τι είναι:** Το κεντρικό αρχείο περιβαλλοντικών μεταβλητών για ΟΛΟ το project.  
**Τι κάνει:** Περιέχει ΟΛΑ τα configuration values:
- **Domain settings:** `DOMAIN`, `FRONTEND_HOST`, `ENVIRONMENT`
- **Project identity:** `PROJECT_NAME`, `STACK_NAME`
- **Backend security:** `SECRET_KEY`, `BACKEND_CORS_ORIGINS`
- **Auth:** `FIRST_SUPERUSER`, `FIRST_SUPERUSER_PASSWORD`
- **Email (SMTP):** `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`, κλπ.
- **PostgreSQL:** `POSTGRES_SERVER`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- **Monitoring:** `SENTRY_DSN`
- **Docker:** `DOCKER_IMAGE_BACKEND`, `DOCKER_IMAGE_FRONTEND`
- **AI API Keys:** `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `TAVILY_API_KEY`

> Αυτό το αρχείο **ΔΕΝ πρέπει** να γίνει commit σε public repos — περιέχει μυστικά κλειδιά!

---

### `.gitattributes`
**Τι είναι:** Κανόνες Git για τον χειρισμό αρχείων.  
**Τι κάνει:** 
- `* text=auto` → Αυτόματη αναγνώριση text/binary αρχείων
- `*.sh text eol=lf` → Τα shell scripts διατηρούν πάντα Unix line endings (LF)

---

### `.gitignore` (root)
**Τι είναι:** Καθορίζει ποια αρχεία/φάκελοι αγνοούνται από το Git.  
**Τι κάνει:** Αγνοεί:
- `.vscode/*` (εκτός `extensions.json`)
- `node_modules/`
- Playwright reports & cache directories

---

### `.pre-commit-config.yaml`
**Τι είναι:** Configuration για το εργαλείο [pre-commit](https://pre-commit.com/).  
**Τι κάνει:** Εκτελεί αυτοματοποιημένους ελέγχους **πριν** κάθε `git commit`:
1. **Pre-commit-hooks:** Ελέγχει μεγάλα αρχεία, TOML/YAML σύνταξη, trailing whitespace, end-of-file fixes
2. **Biome check:** Linting/formatting του frontend κώδικα
3. **Ruff check:** Python linting (PEP8, imports, bugs)
4. **Ruff format:** Python auto-formatting
5. **Mypy:** Static type checking για Python
6. **ty:** Πρόσθετος type checker
7. **Generate Frontend SDK:** Αυτόματη αναγέννηση του frontend API client
8. **Add release date:** Προσθέτει ημερομηνία στο release-notes.md
9. **Zizmor:** Ασφάλεια GitHub Actions workflows

---

### `pyproject.toml` (root)
**Τι είναι:** Root-level Python workspace configuration (uv).  
**Τι κάνει:** 
- Ορίζει ότι ο φάκελος `backend/` είναι μέλος του uv workspace
- Προσθέτει dev dependencies: `zizmor` (GH Actions security)
- Προσθέτει github-actions dependency group: `smokeshow` (coverage reports)

---

### `package.json` (root)
**Τι είναι:** Root-level Node.js workspace configuration (bun).  
**Τι κάνει:**
- Ορίζει το `frontend/` ως workspace member
- Παρέχει shortcut scripts:
  - `npm run dev` → Τρέχει τον Vite dev server
  - `npm run lint` → Frontend linting
  - `npm run test` → Playwright tests
  - `npm run test:ui` → Playwright UI mode

---

### `compose.yml`
**Τι είναι:** Η κύρια Docker Compose configuration (production).  
**Τι κάνει:** Ορίζει 5 services:
1. **`db`** : PostgreSQL 18 container με health checks & persistent volume
2. **`adminer`** : Web-based DB admin tool (σε `adminer.DOMAIN`)
3. **`prestart`** : Εφήμερο container που τρέχει migrations & seed data
4. **`backend`** : FastAPI app με 4 workers, Traefik labels για routing
5. **`frontend`** : Nginx container με το compiled React app

Ορίζει επίσης:
- Volume `app-db-data` για persistent DB storage
- External network `traefik-public` για Traefik routing

---

### `compose.override.yml`
**Τι είναι:** Docker Compose overrides για **τοπικό development**.  
**Τι κάνει:** Αντικαθιστά/προσθέτει ρυθμίσεις:
- **`proxy`** : Traefik σε insecure mode (χωρίς TLS) στο port 80
- **`db`** : Expose port 5432 στο localhost
- **`adminer`** : Expose port 8080
- **`backend`** : Hot-reload mode (`fastapi run --reload`), Docker watch/sync
- **`mailcatcher`** : Fake SMTP server για testing emails (ports 1080, 1025)
- **`frontend`** : Build με `VITE_API_URL=http://localhost:8000`
- **`playwright`** : Container για E2E tests

---

### `compose.traefik.yml`
**Τι είναι:** Ξεχωριστό Docker Compose αρχείο για τον Traefik reverse proxy.  
**Τι κάνει:** Ρυθμίζει τον Traefik σε production mode:
- Let's Encrypt TLS certificates (αυτόματα)
- HTTP → HTTPS redirection
- Basic auth για το Traefik dashboard
- Volumes για certificate storage

---

### `copier.yml`
**Τι είναι:** Configuration για το [Copier](https://copier.readthedocs.io/) template engine.  
**Τι κάνει:** Επιτρέπει τη δημιουργία νέων projects από αυτό το template. Ρωτάει:
- Project name, stack name
- Secret key, superuser credentials
- SMTP settings
- PostgreSQL password
- Sentry DSN

Αποκλείει caches, node_modules, .venv κλπ. από τα generated projects.

---

### `bun.lock`
**Τι είναι:** Lock file του Bun package manager.  
**Τι κάνει:** Κλειδώνει τις ακριβείς εκδόσεις ΟΛΩΝ των npm dependencies, εξασφαλίζοντας reproducible builds.

---

### `uv.lock`
**Τι είναι:** Lock file του uv Python package manager.  
**Τι κάνει:** Κλειδώνει τις ακριβείς εκδόσεις ΟΛΩΝ των Python dependencies.

---

### `LICENSE`
**Τι είναι:** Άδεια χρήσης MIT.  
**Τι κάνει:** Επιτρέπει ελεύθερη χρήση, τροποποίηση και διανομή.

---

### `README.md`
**Τι είναι:** Κύρια τεκμηρίωση του project.  
**Τι κάνει:** Παρέχει overview, screenshots, οδηγίες εγκατάστασης & links.

---

### `CONTRIBUTING.md`
**Τι είναι:** Οδηγός συνεισφοράς.  
**Τι κάνει:** Εξηγεί πώς να κάνεις contribute (PRs, issues, coding standards).

---

### `deployment.md`
**Τι είναι:** Λεπτομερής οδηγός deployment.  
**Τι κάνει:** Βήμα-βήμα οδηγίες για deploy σε production (Docker Swarm, Traefik, DNS).

---

### `development.md`
**Τι είναι:** Οδηγός τοπικής ανάπτυξης.  
**Τι κάνει:** Εξηγεί πώς να στήσεις local dev environment, Docker, κ.α.

---

### `release-notes.md`
**Τι είναι:** Changelog / Release notes.  
**Τι κάνει:** Ιστορικό αλλαγών ανά version.

---

## Φάκελος `.copier/`

### `.copier-answers.yml.jinja`
**Τι είναι:** Jinja template για τις απαντήσεις του Copier.  
**Τι κάνει:** Κατά τη δημιουργία ενός νέου project, αποθηκεύει τις απαντήσεις του χρήστη σε JSON.

### `update_dotenv.py`
**Τι είναι:** Python script που ενημερώνει το `.env` αρχείο.  
**Τι κάνει:** Μετά από ένα Copier update, διαβάζει τις νέες τιμές και τις γράφει στο `.env`, χωρίς να χρησιμοποιεί Jinja templates στο `.env` (ώστε να δουλεύει και χωρίς Copier).

---

## Φάκελος `.github/`

### `dependabot.yml`
**Τι είναι:** Configuration για το GitHub Dependabot.  
**Τι κάνει:** Αυτοματοποιεί ενημερώσεις εξαρτήσεων:
- **GitHub Actions** → Daily checks
- **Python (uv)** → Weekly
- **Bun/npm** → Weekly (αγνοεί `@hey-api/openapi-ts`)
- **Docker** → Weekly
- **Docker Compose** → Weekly
- **Pre-commit** → Daily

### `labeler.yml`
**Τι είναι:** Rules για αυτόματο labeling PRs.  
**Τι κάνει:** Προσθέτει labels (`docs`, `internal`) βάσει ποιοι φάκελοι/αρχεία άλλαξαν.

### `workflows/` (14 αρχεία)
**Τι είναι:** GitHub Actions CI/CD pipelines.  
**Τι κάνουν:**

| Workflow | Σκοπός |
|----------|--------|
| `add-to-project.yml` | Αυτόματη προσθήκη issues/PRs σε GitHub Project |
| `deploy-production.yml` | Deploy σε production |
| `deploy-staging.yml` | Deploy σε staging |
| `detect-conflicts.yml` | Ελέγχει merge conflicts σε PRs |
| `guard-dependencies.yml` | Προστατεύει lockfiles, τρέχει αυτόματα updates |
| `issue-manager.yml` | Αυτόματη διαχείριση issues (stale, close, κλπ.) |
| `labeler.yml` | Αυτόματο labeling PRs |
| `latest-changes.yml` | Ενημέρωση release notes |
| `playwright.yml` | E2E tests μέσω Playwright |
| `pre-commit.yml` | Τρέχει pre-commit checks σε CI |
| `smokeshow.yml` | Δημοσιεύει coverage reports |
| `test-backend.yml` | Unit tests backend (pytest) |
| `test-docker-compose.yml` | Smoke test Docker Compose setup |
| `zizmor.yml` | Security audit GitHub Actions workflows |

---

## Φάκελος `.vscode/`

### `extensions.json`
**Τι είναι:** Recommended VS Code extensions.  
**Τι κάνει:** Προτείνει: FastAPI, Biome, TailwindCSS, Ruff, Docker, Playwright, Python, MJML, ty, GitHub Actions, TOML.

### `launch.json`
**Τι είναι:** VS Code debug configurations.  
**Τι κάνει:** Ορίζει 2 debug profiles:
1. **Python Debugger** : Τρέχει το backend μέσω `uvicorn` με `--reload`
2. **Chrome Debugger** : Ανοίγει Chrome στο `http://localhost:5173` για frontend debugging

---

## Φάκελος `hooks/`

### `post_gen_project.py`
**Τι είναι:** Copier post-generation hook.  
**Τι κάνει:** Μετά τη δημιουργία νέου project, μετατρέπει ΟΛΑ τα `.sh` αρχεία σε Unix line endings (LF) — σημαντικό για cross-platform compatibility.

---

## Φάκελος `img/`

**Τι είναι:** Screenshots & graphics για το README.  
**Τι κάνει:** Περιέχει:
- `dashboard.png` / `dashboard-dark.png` : Screenshots του dashboard
- `dashboard-items.png` : Items view
- `docs.png` : API documentation view
- `login.png` : Login page
- `github-social-preview.png` / `.svg` : Social preview image

---

## Φάκελος `scripts/` (root)

### `generate-client.sh`
**Τι είναι:** Script αυτόματης αναγέννησης του frontend API client.  
**Τι κάνει:**
1. Τρέχει τη FastAPI app για να πάρει το OpenAPI schema
2. Μεταφέρει το `openapi.json` στον frontend φάκελο
3. Τρέχει τον openapi-ts code generator
4. Εκτελεί linting στον generated κώδικα

### `test.sh`
**Τι είναι:** Full test pipeline μέσα σε Docker.  
**Τι κάνει:** Build → σηκώνει containers → τρέχει tests → κατεβάζει containers.

### `test-local.sh`
**Τι είναι:** Τοπικό test pipeline.  
**Τι κάνει:** Σαν το `test.sh` αλλά σε Linux καθαρίζει πρώτα τα `__pycache__`.

### `add_latest_release_date.py`
**Τι είναι:** Python script για release notes.  
**Τι κάνει:** Βρίσκει το τελευταίο version header στο `release-notes.md` και αν δεν έχει ημερομηνία, προσθέτει τη σημερινή.

---

## Φάκελος `backend/`

### Backend Root Αρχεία

#### `pyproject.toml`
**Τι είναι:** Python project configuration & dependency list.  
**Τι κάνει:** Ορίζει:
- **Project metadata:** name=`app`, version=`0.1.0`, Python ≥ 3.10
- **Dependencies:** alembic, email-validator, fastapi, httpx, jinja2, LangChain, psycopg, pydantic, sqlmodel, tenacity, κ.α.
- **Dev dependencies:** coverage, mypy, pytest, ruff, ty
- **Tool configs:** coverage, mypy, ruff (lint rules), ty

#### `Dockerfile`
**Τι είναι:** Docker image definition για το backend.  
**Τι κάνει:**
1. Base: `python:3.10`
2. Εγκαθιστά `uv` (package manager) από official image
3. Εγκαθιστά dependencies σε cached layers
4. Αντιγράφει scripts, config, app code
5. Τελικό command: `fastapi run --workers 4 app/main.py`

#### `alembic.ini`
**Τι είναι:** Configuration αρχείο για το Alembic.  
**Τι κάνει:** Ρυθμίζει:
- Τοποθεσία migration scripts: `app/alembic`
- Logging levels (root=WARN, sqlalchemy=WARN, alembic=INFO)
- Console handler format

#### `.dockerignore`
**Τι είναι:** Αρχεία που αγνοούνται κατά το Docker build.  
**Τι κάνει:** Αποκλείει: `__pycache__`, `.pyc`, `.mypy_cache`, `.venv`, `htmlcov`, `.coverage`

#### `.gitignore`
**Τι είναι:** Backend-specific Git ignore.  
**Τι κάνει:** Αποκλείει: `__pycache__`, `.pyc`, `.mypy_cache`, `.venv`, `htmlcov`, `.cache`, `.coverage`

#### `README.md`
**Τι είναι:** Backend documentation.  
**Τι κάνει:** Εξηγεί τη δομή, τα API endpoints, και πώς να τρέξεις/τεστάρεις.

#### `gradio_app.py`
**Τι είναι:** Εναλλακτικό Chat UI με Gradio.  
**Τι κάνει:** Παρέχει ένα web-based chat interface χωρίς να χρειάζεται το React frontend:
- **Login view:** Email/password authentication μέσω του FastAPI backend
- **Chat view:** Επιλογή/δημιουργία search sessions, αποστολή μηνυμάτων στον AI agent
- **API helpers:** `api_login()`, `api_create_session()`, `api_chat()`, `api_list_sessions()`
- **Styling:** Custom dark theme (indigo/violet), glassmorphism, gradient buttons
- **Τρέχει:** `python gradio_app.py` στο port 9987

---

### Backend `app/` — Κύριος κώδικας

#### `__init__.py`
**Τι είναι:** Python package marker.  
**Τι κάνει:** Κάνει τον φάκελο `app/` importable ως Python package.

#### `main.py`
**Τι είναι:** Entry point της FastAPI εφαρμογής.  
**Τι κάνει:**
1. Αρχικοποιεί **Sentry** monitoring (μόνο σε non-local environments)
2. Δημιουργεί την `app = FastAPI(...)` instance με custom OpenAPI ID generation
3. Ρυθμίζει **CORS middleware** — επιτρέπει requests από configured origins
4. Καταχωρεί τον κεντρικό `api_router` κάτω από `/api/v1`

#### `models.py`
**Τι είναι:** ΟΛΑ τα data models & schemas σε ένα αρχείο.  
**Τι κάνει:** Ορίζει:

**User Models:**
- `UserBase` : Βασικά πεδία (email, is_active, is_superuser, full_name)
- `UserCreate` : Δημιουργία χρήστη (+ password)
- `UserRegister` : Self-registration (email, password, full_name)
- `UserUpdate` : Ενημέρωση χρήστη
- `UserUpdateMe` : Self-update (μόνο full_name, email)
- `UpdatePassword` : Αλλαγή κωδικού
- `User` — **DB Table** (id, hashed_password, created_at, relationships)
- `UserPublic` — API response schema
- `UsersPublic` — Paginated list

**Item Models:**
- `ItemBase`, `ItemCreate`, `ItemUpdate` — CRUD schemas
- `Item` — **DB Table** (id, created_at, owner_id → User)
- `ItemPublic`, `ItemsPublic` — API response schemas

**Auth Models:**
- `Token` : JWT access token response
- `TokenPayload` : JWT token contents
- `NewPassword` : Reset password request
- `Message` : Generic message response

**Todo Models:**
- `TodoBase`, `TodoCreate`, `TodoUpdate` : CRUD schemas
- `Todo` : DB Table (id, created_at, completed, owner_id → User)
- `TodoPublic`, `TodosPublic` : API response schemas

**Search Agent Models:**
- `SearchSessionBase`, `SearchSessionCreate`, `SearchSessionUpdate` : Session CRUD
- `SearchSession` : **DB Table** (id, owner_id, memory JSON, timestamps)
- `SearchHistory` : **DB Table** (id, session_id, owner_id, query, result)
- `AgentChatRequest` : Incoming chat message
- `AgentChatResponse` : Agent reply with session_id

#### `crud.py`
**Τι είναι:** CRUD (Create-Read-Update-Delete) operations.  
**Τι κάνει:**
- `create_user()` : Δημιουργεί user με hashed password
- `update_user()` : Ενημερώνει user (hash αν αλλάξει password)
- `get_user_by_email()` : Αναζήτηση user βάσει email
- `authenticate()` : Ελέγχει email+password, προστατεύει από **timing attacks** (DUMMY_HASH)
- `create_item()` : Δημιουργεί item με owner_id

#### `utils.py`
**Τι είναι:** Βοηθητικές συναρτήσεις (email & tokens).  
**Τι κάνει:**
- `EmailData` : Dataclass για email content
- `render_email_template()` : Renders Jinja2 HTML templates
- `send_email()` : Στέλνει email μέσω SMTP (TLS/SSL)
- `generate_test_email()` : Δημιουργεί test email
- `generate_reset_password_email()` : Email για password reset
- `generate_new_account_email()` : Email νέου λογαριασμού
- `generate_password_reset_token()` : JWT token για reset
- `verify_password_reset_token()` : Επαληθεύει reset token

#### `backend_pre_start.py`
**Τι είναι:** Script ελέγχου ετοιμότητας DB.  
**Τι κάνει:** Δοκιμάζει να συνδεθεί στη βάση (max 5 λεπτά, retry κάθε 1 δευτ.) : χρησιμοποιεί `tenacity` για retries. Τρέχει πριν ξεκινήσει το backend.

#### `initial_data.py`
**Τι είναι:** Script αρχικοποίησης δεδομένων.  
**Τι κάνει:** Καλεί `init_db()` που δημιουργεί τον **first superuser** αν δεν υπάρχει ήδη.

#### `tests_pre_start.py`
**Τι είναι:** Pre-test DB readiness check.  
**Τι κάνει:** Ίδια λογική με `backend_pre_start.py` : ελέγχει ότι η DB είναι online πριν τρέξουν τα tests.

---

### Backend `app/core/`

#### `__init__.py`
**Τι είναι:** Package marker.

#### `config.py`
**Τι είναι:** Κεντρικό configuration μέσω Pydantic Settings.  
**Τι κάνει:** Η κλάση `Settings` φορτώνει μεταβλητές από `.env` + environment:
- **API:** `API_V1_STR = "/api/v1"`
- **Security:** `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES` (8 ημέρες)
- **CORS:** Computed property `all_cors_origins`
- **Database:** Computed `SQLALCHEMY_DATABASE_URI` (PostgreSQL)
- **SMTP:** TLS, SSL, host, port, user, password
- **Email:** `emails_enabled` computed property
- **AI:** `OPENAI_API_KEY`, `TAVILY_API_KEY`
- **Validators:** Ελέγχει ότι τα secrets δεν είναι "changethis" σε production
- **Custom priority:** `.env` file ΠΡΟ περιβαλλοντικών μεταβλητών

#### `db.py`
**Τι είναι:** Database engine & initialization.  
**Τι κάνει:**
- Δημιουργεί το SQLAlchemy `engine` από τo `SQLALCHEMY_DATABASE_URI`
- `init_db()` — Ελέγχει αν υπάρχει ο πρώτος superuser και τον δημιουργεί αν χρειάζεται

#### `security.py`
**Τι είναι:** Security utilities (JWT + Password hashing).  
**Τι κάνει:**
- **Password hashing:** Χρησιμοποιεί Argon2 (κύριο) + bcrypt (fallback) μέσω `pwdlib`
- `create_access_token()` — Δημιουργεί JWT token (HS256)
- `verify_password()` — Ελέγχει password + auto-upgrades hash αν χρειάζεται
- `get_password_hash()` — Hash νέου password

---

### Backend `app/api/`

#### `__init__.py`
**Τι είναι:** Package marker.

#### `main.py`
**Τι είναι:** Κεντρικός router aggregator.  
**Τι κάνει:** Συνδέει ΟΛΟΥΣ τους sub-routers στον κεντρικό `api_router`:
- `login.router` : Authentication endpoints
- `users.router` : User CRUD
- `utils.router` : Health check & test email
- `items.router` : Items CRUD
- `todos.router` : Todos CRUD
- `searches.router` : AI Search agent endpoints
- `private.router` : Μόνο σε local environment (test user creation)

#### `deps.py`
**Τι είναι:** FastAPI dependency injection.  
**Τι κάνει:** Ορίζει reusable dependencies:
- `get_db()` : Generator που δίνει SQLModel `Session`
- `SessionDep` : Annotated type alias για DB session injection
- `TokenDep` : Annotated type alias για OAuth2 token injection
- `get_current_user()` : Αποκωδικοποιεί JWT, επιστρέφει τον User (ή 403/404)
- `CurrentUser` : Annotated type alias για current user injection
- `get_current_active_superuser()` : Ελέγχει ότι ο user είναι superuser

---

### Backend `app/api/routes/`

#### `__init__.py`
**Τι είναι:** Package marker.

#### `login.py`
**Τι είναι:** Authentication endpoints.  
**Τι κάνει:**
- `POST /login/access-token` : OAuth2 login, επιστρέφει JWT token
- `POST /login/test-token` : Τεστ ότι το token λειτουργεί
- `POST /password-recovery/{email}` : Στέλνει email recovery (anti-enumeration protection)
- `POST /reset-password/` : Αλλαγή password μέσω token
- `POST /password-recovery-html-content/{email}` : HTML preview email (μόνο superuser)

#### `users.py`
**Τι είναι:** User management endpoints.  
**Τι κάνει:**
- `GET /users/` : Λίστα users (μόνο superuser)
- `POST /users/` : Δημιουργία user (μόνο superuser)
- `PATCH /users/me` : Update δικά σου στοιχεία
- `PATCH /users/me/password` : Αλλαγή password
- `GET /users/me` : Πάρε τα στοιχεία σου
- `DELETE /users/me` : Διαγραφή λογαριασμού (όχι superuser)
- `POST /users/signup` : Self-registration (public)
- `GET /users/{user_id}` : Πάρε user βάσει ID
- `PATCH /users/{user_id}` : Update user (μόνο superuser)
- `DELETE /users/{user_id}` : Διαγραφή user (μόνο superuser)

#### `items.py`
**Τι είναι:** Items CRUD endpoints.  
**Τι κάνει:**
- `GET /items/` : Λίστα items (superuser βλέπει ΟΛΑ, κανονικός βλέπει τα δικά του)
- `GET /items/{id}` : Ένα item (ownership check)
- `POST /items/` : Δημιουργία item
- `PUT /items/{id}` : Ενημέρωση item
- `DELETE /items/{id}` : Διαγραφή item

#### `todos.py`
**Τι είναι:** Todos CRUD endpoints.  
**Τι κάνει:** Ίδια λογική με items:
- `GET /todos/`, `GET /todos/{id}`
- `POST /todos/`, `PUT /todos/{id}`, `DELETE /todos/{id}`
- Ownership checks, superuser privileges

#### `searches.py`
**Τι είναι:** AI Search Agent endpoints.  
**Τι κάνει:**
- `GET /searches/` : Λίστα search sessions
- `POST /searches/` : Δημιουργία νέας search session
- `POST /searches/{id}/chat` : Στέλνει μήνυμα στον AI agent μέσα σε ένα session. Καλεί `run_agent_on_session()` που τρέχει τον LangChain agent με memory.

#### `private.py`
**Τι είναι:** Private/internal endpoints (μόνο local).  
**Τι κάνει:** `POST /private/users/` : Δημιουργεί users χωρίς authentication (για testing μόνο).

#### `utils.py`
**Τι είναι:** Utility endpoints.  
**Τι κάνει:**
- `POST /utils/test-email/` : Στέλνει test email (μόνο superuser)
- `GET /utils/health-check/` : Health check endpoint (επιστρέφει `true`)

---

### Backend `app/agent/`

#### `graph.py`
**Τι είναι:** Ο κεντρικός AI Search Agent.  
**Τι κάνει:**
1. **LLM Setup:** `ChatOpenAI(model="gpt-4o-mini", temperature=0.2)`
2. **Agent Creation:** `create_agent()` με system prompt + web_search tool
3. **Memory Management:**
   - `_load_memory_from_session()` : Φορτώνει JSON memory από DB
   - `_convert_to_lc_messages()` : Μετατρέπει σε LangChain messages
   - `_append_and_trim_memory()` : Κρατάει τα τελευταία 50 messages
   - `_save_memory_to_session()` : Αποθηκεύει πίσω στη DB
4. **Execution:** `run_agent_on_session()`:
   - Φορτώνει memory → Μετατρέπει → Invoke agent → Εξάγει reply
   - Ενημερώνει memory → Αποθηκεύει search history στη DB

#### `tools.py`
**Τι είναι:** 🛠 Εργαλεία που χρησιμοποιεί ο agent.  
**Τι κάνει:**
- Αρχικοποιεί `TavilySearch` (max_results=3, include_answer=True)
- `web_search(query)` — @tool decorated function:
  - Αναζητά στο web μέσω Tavily API
  - Επιστρέφει JSON-serialized αποτελέσματα
  - Graceful error handling

---

### Backend `app/alembic/`

#### `README`
**Τι είναι:** Σύντομη εξήγηση.  
**Τι κάνει:** Λέει "Generic single-database configuration".

#### `env.py`
**Τι είναι:** Alembic environment configuration.  
**Τι κάνει:**
- Φορτώνει τα SQLModel models (metadata)
- Συνδέεται στη DB μέσω `settings.SQLALCHEMY_DATABASE_URI`
- Υποστηρίζει offline & online migrations

#### `script.py.mako`
**Τι είναι:** Mako template για νέα migration scripts.  
**Τι κάνει:** Δημιουργεί τη δομή κάθε νέου migration file (revision ID, upgrade/downgrade functions).

#### `versions/` (9 migrations)
**Τι είναι:** Ιστορικό database migrations.  
**Τι κάνουν:**

| Migration | Σκοπός |
|-----------|--------|
| `89b749bb3333_initial_schema.py` | Αρχικό schema |
| `e2412789c190_initialize_models.py` | Αρχικοποίηση models |
| `d98dd8ec85a3_edit_replace_id_integers...py` | UUID αντί integers σε IDs |
| `fe56fa70289e_add_created_at...py` | Πεδίο `created_at` σε User/Item |
| `9c0a54914c78_add_max_length...py` | Max length constraints σε strings |
| `1a31ce608336_add_cascade_delete...py` | Cascade delete relationships |
| `9e038bf14c24_todos_table_added.py` | Νέος πίνακας Todos |
| `f0b57bb0e08e_todos_table_updated.py` | Ενημέρωση Todos table |
| `d3236dee0c37_tavily_searches_added.py` | Πίνακες SearchSession & SearchHistory |

---

### Backend `app/email-templates/`

#### `src/` : MJML Sources
- `new_account.mjml` : Template νέου λογαριασμού
- `reset_password.mjml` : Template επαναφοράς κωδικού
- `test_email.mjml` : Template δοκιμαστικού email

#### `build/` : Compiled HTML
- `new_account.html` : Compiled HTML από MJML
- `reset_password.html` : Compiled HTML
- `test_email.html` : Compiled HTML

> Τα MJML αρχεία μετατρέπονται σε HTML. Ο Python κώδικας χρησιμοποιεί μόνο τα HTML αρχεία.

---

### Backend `scripts/`

#### `prestart.sh`
**Τι είναι:** Pre-start script (τρέχει πριν το backend).  
**Τι κάνει:**
1. Ελέγχει αν η DB είναι έτοιμη (`backend_pre_start.py`)
2. Τρέχει Alembic migrations (`alembic upgrade head`)
3. Δημιουργεί initial data (`initial_data.py`)

#### `test.sh`
**Τι είναι:** Test runner.  
**Τι κάνει:** Τρέχει pytest μέσω coverage, δημιουργεί reports.

#### `tests-start.sh`
**Τι είναι:** Full test startup.  
**Τι κάνει:** Ελέγχει DB readiness → Τρέχει tests.

#### `lint.sh`
**Τι είναι:** Linting script.  
**Τι κάνει:** Τρέχει: mypy → ty → ruff check → ruff format check.

#### `format.sh`
**Τι είναι:** Auto-formatting script.  
**Τι κάνει:** Τρέχει: ruff check (fix) → ruff format.

---

### Backend `tests/`

#### `conftest.py`
**Τι είναι:** Pytest configuration & fixtures.  
**Τι κάνει:** Ρυθμίζει shared test fixtures (test client, DB session, test users).

#### `tests/api/routes/`
| Αρχείο | Τι τεστάρει |
|--------|-------------|
| `test_login.py` | Login, token validation, password recovery |
| `test_users.py` | User CRUD (create, read, update, delete) |
| `test_items.py` | Item CRUD operations |
| `test_private.py` | Private endpoint (internal user creation) |

#### `tests/crud/`
| Αρχείο | Τι τεστάρει |
|--------|-------------|
| `test_user.py` | User CRUD functions directly |

#### `tests/scripts/`
| Αρχείο | Τι τεστάρει |
|--------|-------------|
| `test_backend_pre_start.py` | Backend pre-start logic |
| `test_test_pre_start.py` | Tests pre-start logic |

#### `tests/utils/`
| Αρχείο | Τι κάνει |
|--------|----------|
| `item.py` | Helper — δημιουργεί random items |
| `user.py` | Helper — δημιουργεί random users, auth headers |
| `utils.py` | Helper — random email/password generators |

---

## Φάκελος `frontend/`

### Frontend Root Αρχεία

#### `package.json`
**Τι είναι:** NPM/Bun dependencies & scripts.  
**Τι κάνει:**
- **Scripts:** `dev`, `build`, `lint`, `generate-client`, `test`
- **Key dependencies:** React 19, TanStack (Router, Query, Table), Radix UI, TailwindCSS 4, Zod, react-hook-form, Axios, shadcn components
- **Dev dependencies:** Biome (linter), TypeScript 5.9, Vite 7, Playwright

#### `index.html`
**Τι είναι:** HTML entry point (SPA).  
**Τι κάνει:** Φορτώνει το React app μέσα στο `<div id="root">`. Vite αντικαθιστά modules at build time.

#### `vite.config.ts`
**Τι είναι:** Vite bundler configuration.  
**Τι κάνει:**
- **Alias:** `@` → `./src` (short imports)
- **Plugins:** TanStack Router (auto code-splitting), React SWC, TailwindCSS

#### `tsconfig.json`
**Τι είναι:** TypeScript compiler options.  
**Τι κάνει:** ES2020, strict mode, JSX react-jsx, path aliases (`@/*` → `./src/*`).

#### `tsconfig.build.json`
**Τι είναι:** Build-specific TS config.  
**Τι κάνει:** Extends `tsconfig.json` μόνο για production builds.

#### `tsconfig.node.json`
**Τι είναι:** Node-specific TS config.  
**Τι κάνει:** Ρυθμίσεις για Node.js context (Vite config, scripts).

#### `biome.json`
**Τι είναι:** Biome linter/formatter config.  
**Τι κάνει:**
- Auto-organize imports
- Recommended lint rules + custom overrides
- Εξαιρεί auto-generated files (client, routeTree, UI components)
- Double quotes, space indentation

#### `components.json`
**Τι είναι:** shadcn/ui configuration.  
**Τι κάνει:** Ρυθμίζει:
- Style: "new-york"
- CSS Variables
- Icon library: Lucide
- Path aliases: `@/components`, `@/lib/utils`, `@/hooks`

#### `openapi-ts.config.ts`
**Τι είναι:** OpenAPI TypeScript code generator config.  
**Τι κάνει:**
- Input: `openapi.json` (generated από το backend)
- Output: `./src/client/`
- Plugins: Axios client, SDK classes, JSON schemas

#### `Dockerfile`
**Τι είναι:** Multi-stage Docker build.  
**Τι κάνει:**
1. **Stage 1 (build):** Bun install → build React app
2. **Stage 2 (serve):** Nginx container με τα compiled static files

#### `Dockerfile.playwright`
**Τι είναι:** Docker image για E2E tests.  
**Τι κάνει:** Microsoft Playwright base image + Bun install + app files.

#### `nginx.conf`
**Τι είναι:** Nginx configuration.  
**Τι κάνει:** SPA routing — try files, fallback στο `index.html` (για client-side routing).

#### `nginx-backend-not-found.conf`
**Τι είναι:** Extra Nginx config.  
**Τι κάνει:** Επιστρέφει 404 για `/api`, `/docs`, `/redoc` — αποτρέπει direct access μέσω frontend container.

#### `playwright.config.ts`
**Τι είναι:** Playwright E2E test configuration.  
**Τι κάνει:**
- Test directory: `./tests`
- Base URL: `http://localhost:5173`
- Browser: Chromium μόνο (Firefox/Safari σε comments)
- Auth setup project
- Auto-start dev server

#### `.env`
**Τι είναι:** Frontend environment variables.  
**Τι κάνει:** `VITE_API_URL=http://localhost:8000`, `MAILCATCHER_HOST=http://localhost:1080`

#### `.gitignore` / `.dockerignore`
**Τι κάνουν:** Αγνοούν build artifacts, node_modules, Playwright reports.

---

### Frontend `src/`

#### `main.tsx`
**Τι είναι:** React entry point.  
**Τι κάνει:**
1. Ρυθμίζει **OpenAPI client** (base URL, auto-token injection from localStorage)
2. Δημιουργεί **QueryClient** με auto-logout σε 401/403
3. Δημιουργεί **Router** (TanStack Router, file-based)
4. Renders:
   - `ThemeProvider` (dark mode default)
   - `QueryClientProvider`
   - `RouterProvider`
   - `Toaster` (sonner notifications)

#### `index.css`
**Τι είναι:** Global CSS + TailwindCSS design tokens.  
**Τι κάνει:** Ορίζει CSS variables για colors, radii, sidebar, charts — light & dark themes.

#### `utils.ts`
**Τι είναι:** Utility functions.  
**Τι κάνει:**
- `extractErrorMessage()` — Εξάγει error message από API errors
- `handleError()` — Global error handler (δείχνει toast)
- `getInitials()` — Εξάγει αρχικά από ονοματεπώνυμο (π.χ. "Πάνος Κ." → "ΠΚ")

#### `vite-env.d.ts`
**Τι είναι:** TypeScript declarations για Vite.  
**Τι κάνει:** Δηλώνει τα `import.meta.env` types.

#### `routeTree.gen.ts`
**Τι είναι:** Auto-generated route tree.  
**Τι κάνει:** Δημιουργείται αυτόματα από τον TanStack Router plugin — αντιστοιχίζει file-based routes σε route objects.

---

### Frontend `src/client/`

> **Auto-generated** — ΟΛΑ τα αρχεία εδώ δημιουργούνται αυτόματα από το `openapi-ts`.

#### `index.ts`
**Τι είναι:** Re-exports barrel.  
**Τι κάνει:** Εξάγει: `ApiError`, `CancelablePromise`, `OpenAPI`, SDK services, types.

#### `types.gen.ts`
**Τι είναι:** TypeScript types.  
**Τι κάνει:** Ορίζει TypeScript interfaces για ΟΛΑ τα API request/response models.

#### `schemas.gen.ts`
**Τι είναι:** JSON Schemas.  
**Τι κάνει:** Runtime validation schemas αντίστοιχα με τα Pydantic models.

#### `sdk.gen.ts`
**Τι είναι:** SDK service classes.  
**Τι κάνει:** TypeScript classes (LoginService, UsersService, ItemsService, κλπ.) που καλούν τα API endpoints μέσω Axios.

#### `core/ApiError.ts`
**Τι είναι:** Custom error class.  
**Τι κάνει:** Extends Error με HTTP status, body, request details.

#### `core/ApiRequestOptions.ts`
**Τι είναι:** Request options type.  
**Τι κάνει:** Ορίζει structure για API request configuration.

#### `core/ApiResult.ts`
**Τι είναι:** Response result type.

#### `core/CancelablePromise.ts`
**Τι είναι:** Cancelable Promise implementation.  
**Τι κάνει:** Wrapper γύρω από Promises που υποστηρίζει cancellation.

#### `core/OpenAPI.ts`
**Τι είναι:** OpenAPI client configuration.  
**Τι κάνει:** Stores BASE URL, TOKEN resolver, HEADERS.

#### `core/request.ts`
**Τι είναι:** HTTP request handler.  
**Τι κάνει:** Κεντρικός Axios request handler — builds URLs, sets headers, handles errors.

---

### Frontend `src/components/`

#### `theme-provider.tsx`
**Τι είναι:** Theme context provider (light/dark mode).  
**Τι κάνει:** Χρησιμοποιεί `next-themes` για:
- Αποθήκευση theme preference σε localStorage
- Auto-detect system theme
- Εφαρμογή CSS class στο document root

#### `ui/` (24 components — shadcn/ui)
**Τι είναι:** 🧩 Reusable UI component library βασισμένη σε shadcn/ui.

| Component | Σκοπός |
|-----------|--------|
| `alert.tsx` | Alert notifications (variants: default, destructive) |
| `avatar.tsx` | User avatar με fallback initials |
| `badge.tsx` | Status badges (default, secondary, destructive, outline) |
| `button.tsx` | Button variants (primary, secondary, ghost, outline, link) |
| `button-group.tsx` | Grouped buttons |
| `card.tsx` | Card containers (header, title, description, content, footer) |
| `checkbox.tsx` | Checkbox input |
| `dialog.tsx` | Modal dialogs |
| `dropdown-menu.tsx` | Dropdown menus (items, checkboxes, radio groups) |
| `form.tsx` | Form components (react-hook-form integration) |
| `input.tsx` | Text input field |
| `label.tsx` | Form label |
| `loading-button.tsx` | Button with loading spinner |
| `pagination.tsx` | Table pagination controls |
| `password-input.tsx` | Password field with show/hide toggle |
| `select.tsx` | Select dropdown |
| `separator.tsx` | Visual separator line |
| `sheet.tsx` | Slide-out panel (left/right/top/bottom) |
| `sidebar.tsx` | Collapsible sidebar component (πολύπλοκο, ~23KB) |
| `skeleton.tsx` | Loading skeleton placeholder |
| `sonner.tsx` | Toast notifications (via sonner library) |
| `table.tsx` | Data table (header, body, row, cell, caption) |
| `tabs.tsx` | Tab navigation |
| `tooltip.tsx` | Hover tooltips |

#### `Admin/`
| Component | Σκοπός |
|-----------|--------|
| `AddUser.tsx` | Modal φόρμα δημιουργίας χρήστη |
| `EditUser.tsx` | Modal φόρμα επεξεργασίας χρήστη |
| `DeleteUser.tsx` | Confirmation dialog διαγραφής χρήστη |
| `UserActionsMenu.tsx` | Dropdown menu ενεργειών (Edit, Delete) |
| `columns.tsx` | TanStack Table column definitions για users |

#### `Items/`
| Component | Σκοπός |
|-----------|--------|
| `AddItem.tsx` | Modal φόρμα δημιουργίας item |
| `EditItem.tsx` | Modal φόρμα επεξεργασίας item |
| `DeleteItem.tsx` | Confirmation dialog διαγραφής item |
| `ItemActionsMenu.tsx` | Dropdown menu ενεργειών |
| `columns.tsx` | TanStack Table column definitions για items |

#### `Common/`
| Component | Σκοπός |
|-----------|--------|
| `Appearance.tsx` | Theme switcher (light/dark/system) |
| `AuthLayout.tsx` | Layout wrapper για login/signup σελίδες |
| `DataTable.tsx` | Generic data table component (sorting, pagination) |
| `ErrorComponent.tsx` | Global error boundary display |
| `Footer.tsx` | App footer |
| `Logo.tsx` | App logo (SVG) |
| `NotFound.tsx` | 404 page |

#### `Pending/`
| Component | Σκοπός |
|-----------|--------|
| `PendingItems.tsx` | Loading skeleton για items |
| `PendingUsers.tsx` | Loading skeleton για users |

#### `Sidebar/`
| Component | Σκοπός |
|-----------|--------|
| `AppSidebar.tsx` | Κύριο sidebar component (navigation menu) |
| `Main.tsx` | Main navigation links (Dashboard, Items) |
| `User.tsx` | User menu στο sidebar (settings, logout) |

#### `UserSettings/`
| Component | Σκοπός |
|-----------|--------|
| `UserInformation.tsx` | Εμφάνιση/επεξεργασία user info |
| `ChangePassword.tsx` | Αλλαγή password φόρμα |
| `DeleteAccount.tsx` | Button/link για διαγραφή λογαριασμού |
| `DeleteConfirmation.tsx` | Confirmation dialog |

---

### Frontend `src/hooks/`

#### `useAuth.ts`
**Τι είναι:** Custom hook για authentication.  
**Τι κάνει:**
- `isLoggedIn()` : Ελέγχει localStorage για access token
- `user` : Fetches current user data (React Query)
- `signUpMutation` : Self-registration
- `loginMutation` : Login + store token
- `logout()` : Remove token + redirect

#### `useCopyToClipboard.ts`
**Τι είναι:** Hook για copy-to-clipboard.  
**Τι κάνει:** Provides `copyToClipboard(text)` function + copied state.

#### `useCustomToast.ts`
**Τι είναι:** Custom toast notification hook.  
**Τι κάνει:** Wraps sonner toast library — provides `showErrorToast(message)`.

#### `useMobile.ts`
**Τι είναι:** Mobile detection hook.  
**Τι κάνει:** Returns `isMobile` boolean based on viewport width (breakpoint: 768px).

---

### Frontend `src/lib/`

#### `utils.ts`
**Τι είναι:** CSS utility function.  
**Τι κάνει:** `cn(...classes)` — Merges Tailwind class names intelligently (clsx + tailwind-merge).

---

### Frontend `src/routes/`

> File-based routing μέσω TanStack Router.

#### `__root.tsx`
**Τι είναι:** Root route (πάντα rendered).  
**Τι κάνει:** Renders:
- `<HeadContent />` : SEO meta tags
- `<Outlet />` : Child routes
- Dev tools (TanStack Router + React Query)
- Custom 404 & Error components

#### `_layout.tsx`
**Τι είναι:** Authenticated layout wrapper.  
**Τι κάνει:**
- `beforeLoad` → Redirect σε `/login` αν δεν είσαι logged in
- Renders sidebar + header + main content + footer

#### `login.tsx`
**Τι είναι:** Login page.  
**Τι κάνει:** Email/password form (Zod validation), redirect αν ήδη logged in.

#### `signup.tsx`
**Τι είναι:** Registration page.  
**Τι κάνει:** Email/password/full_name form με Zod validation.

#### `recover-password.tsx`
**Τι είναι:** Password recovery page.  
**Τι κάνει:** Φόρμα εισαγωγής email για password reset.

#### `reset-password.tsx`
**Τι είναι:** Password reset page.  
**Τι κάνει:** Φόρμα νέου password (token-based from email link).

#### `_layout/index.tsx`
**Τι είναι:** Dashboard home page.  
**Τι κάνει:** Εμφανίζει "Hi, {user name}" welcome message.

#### `_layout/items.tsx`
**Τι είναι:** Items management page.  
**Τι κάνει:** Data table με items + Add button.

#### `_layout/admin.tsx`
**Τι είναι:** Admin user management page.  
**Τι κάνει:** Data table με users (μόνο superuser access).

#### `_layout/settings.tsx`
**Τι είναι:** User settings page.  
**Τι κάνει:** Tabs: User Information, Change Password, Appearance, Danger Zone.

---

### Frontend `tests/`

#### `config.ts`
**Τι είναι:** Test configuration.  
**Τι κάνει:** Shared test settings (API URLs, credentials).

#### `auth.setup.ts`
**Τι είναι:** Playwright auth setup.  
**Τι κάνει:** Logs in before tests, saves auth state.

#### Test Specs:
| Αρχείο | Τι τεστάρει |
|--------|-------------|
| `login.spec.ts` | Login flow, validation, error handling |
| `sign-up.spec.ts` | Registration flow |
| `admin.spec.ts` | Admin user management |
| `items.spec.ts` | Item CRUD through UI |
| `user-settings.spec.ts` | Settings page functionality |
| `reset-password.spec.ts` | Password reset flow |

#### `utils/`
| Αρχείο | Σκοπός |
|--------|--------|
| `mailcatcher.ts` | Helper για ανάγνωση emails από MailCatcher |
| `privateApi.ts` | Direct API calls (bypass UI) |
| `random.ts` | Random data generators |
| `user.ts` | Test user creation helpers |

---

