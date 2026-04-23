# 03 — Request Bodies with Pydantic

Learn how to receive, validate, and constrain JSON data sent by clients in POST/PUT/PATCH requests.

## What You Will Learn

- How to use Pydantic models to define and validate JSON request bodies
- How FastAPI distinguishes between path, query, and body parameters
- How to add field-level constraints with `Field(...)`
- How to compose nested models
- How to write custom validators with `@field_validator` and `@model_validator`

## Files

| File | What It Teaches |
|------|-----------------|
| `basic_body.py` | Pydantic model as a JSON request body |
| `body_path_query.py` | Mixing body + path + query in a single endpoint |
| `field_validation.py` | `Field(...)` constraints: min/max length, regex, numeric ranges |
| `nested_models.py` | Nested Pydantic models (model inside model) |
| `custom_validators.py` | `@field_validator` and `@model_validator` for custom rules |

## How to Run

```bash
# From this directory — pick any file
uvicorn basic_body:app --reload
uvicorn body_path_query:app --reload
uvicorn field_validation:app --reload
uvicorn nested_models:app --reload
uvicorn custom_validators:app --reload
```

Then visit http://127.0.0.1:8000/docs and use the **"Try it out"** button to send JSON payloads.

## Key Concepts

### Pydantic Models as Request Bodies
```python
class Item(BaseModel):
    name: str
    price: float
    in_stock: bool = True   # default value → optional field

@app.post("/items")
def create_item(item: Item):
    return item
```
FastAPI automatically reads the JSON body and validates it against the model.

### How FastAPI Decides What's What
- In the URL path → **path parameter**
- Pydantic model → **request body**
- Everything else → **query parameter**

### Field Validation
```python
username: str = Field(min_length=3, max_length=20, pattern=r"^[a-z0-9_]+$")
age: int = Field(ge=13, le=120)
```

### Custom Validators
```python
@field_validator("email")
@classmethod
def validate_email(cls, v):
    if "@" not in v:
        raise ValueError("Invalid email")
    return v.lower()
```

See `docs/03_request_bodies.md` for the full theory.
