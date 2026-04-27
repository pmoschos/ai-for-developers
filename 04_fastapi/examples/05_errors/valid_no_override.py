from fastapi import FastAPI

app = FastAPI(title="Valid")

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return f"User #{user_id}"