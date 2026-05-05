# Option 1: Using Uvicorn (most common)

```
cd c:\Users\user\Desktop\FastAPI-pmoschos\project01
```

```
uvicorn books:app --reload
```

books: Refers to books.py
app: Refers to the app = FastAPI() object inside your code
--reload: Automatically restarts the server whenever you save changes to your code

# Option 2: Using FastAPI CLI (requires fastapi-cli)

```
cd c:\Users\user\Desktop\FastAPI-pmoschos\project01
```

```
fastapi dev books.py
```

## Use specific port

```
uvicorn books:app --reload --port 8001
```