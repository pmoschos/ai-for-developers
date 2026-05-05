# 📘 Project 3.5 — TodoApp (Alembic Migrations)

> **Difficulty:** ⭐⭐⭐ | **Study Time:** ~45 minutes

## 🎯 What we learn

How do we **change the database structure** without losing data?  
The answer: **Alembic** — a database migrations tool.

### Scenario
In Project 3, the `Users` model did not have a `phone_number`.  
Now we want to **add** this field → we need a **migration**.

## 📁 Structure

```
Project 3.5/
└── TodoApp/
    ├── main.py              # Same as Project 3
    ├── database.py          # Same
    ├── models.py            # + phone_number field!
    ├── routers/
    │   ├── auth.py          # + phone_number in register
    │   ├── todos.py
    │   ├── admin.py
    │   └── users.py         # + update phone endpoint
    └── alembic/
        ├── env.py           # Alembic configuration
        └── versions/        # Migration scripts
```

## 🚀 How Alembic works

### Step 1: Initialization
```bash
cd "Project 3.5/TodoApp"
alembic init alembic
```

### Step 2: Configuration (`alembic/env.py`)
```python
from models import Base
target_metadata = Base.metadata
# + database connection setup
```

### Step 3: Create migration
```bash
# Automatic detection of changes in models
alembic revision --autogenerate -m "add phone_number to users"
```

### Step 4: Apply migration
```bash
alembic upgrade head    # Apply the latest migration
alembic downgrade -1    # Revert the last one
alembic history         # View migration history
```

## 📖 What changed compared to Project 3

### `models.py` — New field
```python
class Users(Base):
    ...
    phone_number = Column(String)    # ← NEW!
```

### `routers/auth.py` — Registration
```python
class CreateUserRequest(BaseModel):
    ...
    phone_number: str                # ← NEW!
```

### `routers/users.py` — New endpoint
```python
@router.put("/phonenumber/{phone_number}")
async def update_phone(phone_number: str, user, db):
    ...
```

## 💡 Why Alembic?

| Without Alembic | With Alembic |
|-----------------|--------------|
| Drop DB + rebuild | Change schema without data loss |
| Manual `ALTER TABLE` | Automatic migration scripts |
| No history tracking | Version control for DB schema |
| Impossible rollback | `alembic downgrade` = undo |

## ⚡ Key Takeaways

1. **Alembic = Git for databases** — Version control for schema.
2. **`--autogenerate`** = Compares models vs DB → creates a migration script automatically.
3. **`upgrade head`** = Apply ALL pending migrations.
4. **`downgrade -1`** = Revert (rollback) — a lifesaver in production!
5. **Small changes** — One migration per change, avoid large batch schemas.

## ➡️ Next: [Project 4](../Project%204/) — Testing with pytest!
