# serve.py
import os

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from dotenv import load_dotenv

from database import query, execute
from embeddings import get_embedding

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
load_dotenv()

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
HOST = "0.0.0.0"
PORT = 8000

# -----------------------------------------------------------------------------
# Init
# -----------------------------------------------------------------------------
app = FastAPI(title="Embedding API", version="1.0")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# -----------------------------------------------------------------------------
# Queries
# -----------------------------------------------------------------------------
async def get_closest_neighbors(question: str, limit: int = 2):
    """Return nearest neighbors in the vector space for a given question."""
    print(f"Searching for neighbors of: '{question}'")
    embedding = await get_embedding(MODEL_NAME, question)
    vector_str = "[" + ",".join(map(str, embedding)) + "]"
    return await query(
        """
        SELECT content
        FROM documents
        ORDER BY embedding <-> $1
        LIMIT $2;
        """,
        vector_str, limit
    )

# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def render_home(request: Request):
    """Render the home page."""
    return templates.TemplateResponse("index.html", {"request": request, "msg": "Hello, World!"})

@app.post("/question", response_class=HTMLResponse)
async def handle_question(request: Request, question: str = Form(...)):
    """Accept a user question and return nearest content matches."""
    answers = await get_closest_neighbors(question)
    return templates.TemplateResponse("index.html", {"request": request, "answers": answers})

# -----------------------------------------------------------------------------
# Startup
# -----------------------------------------------------------------------------
# @app.on_event("startup")
# async def insert_sample_data():
#     content = "North Carolina is a great state"
#     title = "North Carolina"
#     embedding = await get_embedding(content)
#     vector_str = "[" + ",".join(map(str, embedding)) + "]"
#     await execute(
#         """
#         INSERT INTO documents (content, embedding, title)
#         VALUES ($1, $2, $3);
#         """,
#         content, vector_str, title
#     )

# -----------------------------------------------------------------------------
# Entry Point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("serve:app", host=HOST, port=PORT, reload=False)
