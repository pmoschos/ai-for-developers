# 📘 Project 2 — Books API (Pydantic Models)

> **Difficulty:** ⭐⭐ | **File:** `books2.py` | **Study Time:** ~45 minutes

## 🎯 What we learn

We are advancing Project 1 by introducing:
- **Pydantic models** instead of raw dicts → automatic validation
- **`Field()`** validators — min/max values, descriptions
- **Status codes** — `201 Created`, `204 No Content`
- **`HTTPException`** — proper error handling

## 📁 Structure

```
Project 2/
└── books2.py          # Improved API with Pydantic
```

## 🚀 How to run it

```bash
cd "Project 2"
uvicorn books2:app --reload
```

## 📖 Code Analysis

### 1. Data Model — `Book` class (plain Python)
```python
class Book:
    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        ...
```
> Even though it uses a standard Python class (not a dataclass), it holds typed data.

### 2. Request Validation — `BookRequest(BaseModel)`
```python
class BookRequest(BaseModel):
    id: Optional[int] = Field(description='ID is not needed on create', default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)        # 1-5 only!
    published_date: int = Field(gt=1999, lt=2031)
```

> 🔑 **Key concept:** Separate model for input (`BookRequest`) vs internal representation (`Book`).

### 3. Endpoints & Status Codes

| Method | Endpoint | Status Code | Functionality |
|--------|----------|-------------|---------------|
| `GET` | `/books` | 200 | List all |
| `GET` | `/books/{id}` | 200 / 404 | Book by ID |
| `GET` | `/books/?rating=5` | 200 | Filter by rating |
| `GET` | `/books/publish/?date=2024` | 200 | Filter by year |
| `POST` | `/books/create-book` | **201** Created | Create |
| `PUT` | `/books/update-book` | **204** No Content | Update |
| `DELETE` | `/books/{id}` | **204** No Content | Delete |

### 4. Error Handling
```python
@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail='Item not found')
```

### 5. Path & Query Validation
```python
# Path parameter with validation
book_id: int = Path(gt=0)         # Must be > 0

# Query parameter with validation
rating: int = Query(gt=0, lt=6)   # 1-5
```

## 🔍 Key differences from Project 1

| Project 1 | Project 2 |
|-----------|-----------|
| `list[dict]` | `list[Book]` — typed objects |
| No validation | `Field(min_length=3, gt=0)` |
| Always 200 OK | `status_code=201`, `204`, `404` |
| Silent failure | `HTTPException(404, "Not found")` |
| Search by title (string) | Search by ID (int) |
| No auto-increment | `find_book_id()` — auto-generates ID |

## ⚡ Key Takeaways

1. **Pydantic = Automatic validation** — Invalid data → 422 error automatically.
2. **Input ≠ Storage model** — `BookRequest` (API shape) vs `Book` (internal shape).
3. **Status codes matter** — `201` for create, `204` for update/delete.
4. **`HTTPException`** — Correct error messages sent to the client.
5. **`Path()` & `Query()`** — Validation constraints directly on URL parameters.

## ➡️ Next: [Project 3](../Project%203/) — Adding Database + Authentication!
