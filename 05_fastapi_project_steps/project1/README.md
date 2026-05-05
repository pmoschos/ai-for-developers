# 📘 Project 1 — Books API (Basics)

> **Δυσκολία:** ⭐ | **Αρχείο:** `books.py` | **Χρόνος μελέτης:** ~30 λεπτά

## 🎯 Τι μαθαίνουμε

Αυτό είναι το **πρώτο βήμα** στο FastAPI. Δημιουργούμε ένα απλό API χρησιμοποιώντας **dictionaries** (χωρίς Pydantic, χωρίς database).

### Concepts

| Concept | Περιγραφή | Γραμμές |
|---------|-----------|---------|
| `FastAPI()` | Δημιουργία εφαρμογής | `app = FastAPI()` |
| `@app.get()` | GET endpoint — ανάγνωση δεδομένων | Πολλαπλά |
| `@app.post()` | POST endpoint — δημιουργία δεδομένων | `create_book()` |
| `@app.put()` | PUT endpoint — ενημέρωση δεδομένων | `update_book()` |
| `@app.delete()` | DELETE endpoint — διαγραφή δεδομένων | `delete_book()` |
| Path Parameters | `/books/{title}` — τιμή μέσα στο URL | `read_book()` |
| Query Parameters | `/books/?category=science` — φίλτρο στο URL | `read_category_by_query()` |

## 📁 Δομή

```
Project 1/
└── books.py          # Ολόκληρο το API σε ένα αρχείο
```

## 🚀 Πώς το τρέχω

```bash
cd "Project 1"
uvicorn books:app --reload
```

Ανοίξτε: http://localhost:8000/docs

## 📖 Ανάλυση κώδικα

### 1. Data Storage — Απλή λίστα από dicts
```python
BOOKS = [
    {"title": "Title One", "author": "Author One", "category": "science"},
    ...
]
```
> ⚠️ **No database** — τα δεδομένα χάνονται σε κάθε restart!

### 2. CRUD Operations

| HTTP Method | Endpoint | Λειτουργία |
|------------|----------|------------|
| `GET` | `/books` | Λίστα όλων |
| `GET` | `/books/{title}` | Εύρεση βιβλίου |
| `GET` | `/books/?category=X` | Φιλτράρισμα |
| `GET` | `/books/byauthor/` | Αναζήτηση κατά author |
| `POST` | `/books/create_book` | Δημιουργία (body = dict) |
| `PUT` | `/books/update_book` | Ενημέρωση |
| `DELETE` | `/books/delete_book/{title}` | Διαγραφή |

### 3. Path vs Query Parameters
```python
# Path parameter — μέρος του URL
@app.get("/books/{book_title}")
async def read_book(book_title: str):  # /books/Title%20One

# Query parameter — μετά το ?
@app.get("/books/")
async def read_by_query(category: str):  # /books/?category=science
```

## ⚡ Key Takeaways

1. **FastAPI = decorators** — `@app.get("/path")` δημιουργεί endpoint αυτόματα
2. **Swagger UI** — Αυτόματο interactive documentation στο `/docs`
3. **Async by default** — `async def` σε κάθε endpoint
4. **Χωρίς validation** — ο client μπορεί να στείλει ό,τι θέλει (αυτό λύνεται στο Project 2!)

## ➡️ Επόμενο: [Project 2](../Project%202/) — Προσθέτουμε Pydantic validation!
