"""
11 — Middleware: CORS Configuration

Run:  uvicorn examples.11_middleware.cors_example:app --reload

CORS = Cross-Origin Resource Sharing.
If a browser app on a different origin calls your API, you must enable CORS.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="CORS Example")

# Configure CORS — whitelist specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",         # React dev server
        "http://localhost:5173",         # Vite dev server
        "https://myapp.com",             # production frontend
    ],
    allow_credentials=True,              # This is to allow cookies, authorization headers, session information, authentication details, etc.
    allow_methods=["*"],                 # allow all HTTP methods like POST, PUT, GET, DELETE, etc.
    allow_headers=["*"],                 # allow all headers, but in real production, you should specify the allowed headers to enhance security.
)

# Attention: NEVER ship allow_origins=["*"] with allow_credentials=True
#   — it's a security anti-pattern!


@app.get("/")
def root():
    return {"message": "CORS is configured!"}


@app.get("/data")
def data():
    """This endpoint can be called from the whitelisted origins."""
    return {"items": ["a", "b", "c"]}
