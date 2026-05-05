import json
import os
from fastapi import Body, FastAPI

app = FastAPI()

BOOKS = []
# Get the absolute path to the directory containing this file
base_dir = os.path.dirname(os.path.abspath(__file__))
books_file_path = os.path.join(base_dir, "books.jsonl")

example_book = {
    "title": "Foundations of Quantum Systems",
    "author": "Elias Hartman",
    "category": "science"
}

# Load the books from the JSON Lines file
with open(books_file_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            BOOKS.append(json.loads(line))

def save_books():
    with open(books_file_path, "w", encoding="utf-8") as f:
        for book in BOOKS:
            f.write(json.dumps(book) + "\n")


@app.get("/books")
async def read_all_books():
    return BOOKS

# Path parameter χρησιμοποιείς όταν θέλεις να δείξεις ποιο συγκεκριμένο πράγμα ζητάς.
@app.get("/books/{book_title}")
async def read_book(book_title: str):
    for book in BOOKS:
        if book.get('title').casefold() == book_title.casefold():
            return book
    return {'error': 'Book not found'}

# Query parameter χρησιμοποιείς όταν θέλεις να δείξεις με ποια κριτήρια ψάχνεις ή φιλτράρεις.
@app.get("/books/")
async def read_category_by_query(category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('category').casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return


# Get all books from a specific author using path or query parameters
@app.get("/books/byauthor/")
async def read_books_by_author_path(author: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('author').casefold() == author.casefold():
            books_to_return.append(book)

    return books_to_return


@app.get("/books/{book_author}/")
async def read_author_category_by_query(book_author: str, category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('author').casefold() == book_author.casefold() and \
                book.get('category').casefold() == category.casefold():
            books_to_return.append(book)

    return books_to_return

# Το Body() εδώ λέει στο FastAPI
# Πάρε αυτή την τιμή από το request body (JSON body) του HTTP request
@app.post("/books/create_book")
async def create_book(new_book: dict = Body(example=example_book)):
    BOOKS.append(new_book)
    save_books()
    return {'message': 'Book created successfully'}


@app.put("/books/update_book")
async def update_book(updated_book: dict = Body(example=example_book)): 
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == updated_book.get('title').casefold():
            BOOKS[i] = updated_book
    save_books()
    return {'message': 'Book updated successfully'}

@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title: str):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == book_title.casefold():
            BOOKS.pop(i)
            break
    save_books()
    return {'message': 'Book deleted successfully'}
