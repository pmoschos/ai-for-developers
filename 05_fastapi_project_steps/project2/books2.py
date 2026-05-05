from typing import Optional, List
from fastapi import FastAPI, Path, Query, HTTPException, Body
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI()

import json
import os
from dataclasses import dataclass, asdict

# Our Database Model / Entity representing a structured Book object
@dataclass
class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int


# Our Data Transfer Object (DTO) containing validation rules for incoming requests
class BookRequest(BaseModel):
    # Optional field since we auto-generate the ID when creating a new book
    id: Optional[int] = Field(description='ID is not needed on create', default=None)
    # Field validation directly rejecting requests that don't match our specific requirements
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=1999, lt=2031)

    # model_config provides the schema example seen in the Swagger UI interactive docs
    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "AI for Developers",
                "author": "Panagiotis Moschos",
                "description": "Building with Large Language Models",
                "rating": 5,
                'published_date': 2026
            }
        }
    }
        

BOOKS = []
base_dir = os.path.dirname(os.path.abspath(__file__))
books_file_path = os.path.join(base_dir, "books.json")

# On startup: Read the JSON database file into our in-memory list of Book dataclasses
with open(books_file_path, "r", encoding="utf-8") as file:
    books_data = json.load(file)
    for b in books_data:
        BOOKS.append(Book(**b))

# Helper function: Overwrite the JSON database file with our updated list of Book dataclasses 
def save_books():
    with open(books_file_path, "w", encoding="utf-8") as file:
        json.dump([asdict(book) for book in BOOKS], file, indent=4)


@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books() -> List[Book]:
    return BOOKS


# The Path parameter here requires the given book_id to be greater than 0
@app.get("/books/{book_id}", status_code=status.HTTP_200_OK, tags=["Books"])
async def read_book(book_id: int = Path(gt=0)) -> Book:
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail='Item not found')


# Query parameters are automatically extracted from the URL (e.g., /books/?book_rating=5)
@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_book_by_rating(book_rating: int = Query(gt=0, lt=6)) -> List[Book]:
    books_to_return = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)
    return books_to_return


# Extended GET request showcasing automatic Swagger UI documentation generation attributes
@app.get("/books/publish/", status_code=status.HTTP_200_OK, summary="Filter Books by Star Rating", description="Filter Books by Star Rating description", response_description="Successful Response - Books returned", tags=["Books"])
async def read_books_by_publish_date(published_date: int = Query(gt=1999, lt=2031)) -> List[Book]:
    books_to_return = []
    for book in BOOKS:
        if book.published_date == published_date:
            books_to_return.append(book)
    return books_to_return


# POST endpoint expects a validated BookRequest schema via the JSON Body
@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))
    save_books()


# Utility function to auto-increment the ID
def find_book_id(book: Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book


@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = book
            book_changed = True
    if not book_changed:
        raise HTTPException(status_code=404, detail='Item not found')
    save_books()


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            book_changed = True
            break
    if not book_changed:
        raise HTTPException(status_code=404, detail='Item not found')
    save_books()
