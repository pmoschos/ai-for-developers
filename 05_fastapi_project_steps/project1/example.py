import json
import os

# 1. Get the absolute path to example.json
base_dir = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(base_dir, "example.json")

# 2. Read the entire JSON file into a Python list of dictionaries
with open(json_file_path, "r", encoding="utf-8") as file:
    books = json.load(file)

# 3. Print the results to verify it worked
print(f"Successfully loaded {len(books)} books from example.json:\n")

for book in books:
    print(f"- {book['title']} by {book['author']} (Category: {book['category']})")
