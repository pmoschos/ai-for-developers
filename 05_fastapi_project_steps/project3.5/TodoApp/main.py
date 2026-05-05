from fastapi import FastAPI
import models
from database import engine
from routers import auth, todos, admin, users

app = FastAPI()

# This command creates all the tables in the database if they don't already exist
# It uses the Base we created in database.py and the models defined in models.py
models.Base.metadata.create_all(bind=engine)

# Including routers keeps our main.py clean and modular.
# It delegates specific endpoints to their respective files (e.g., auth, todos)
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)