# serve.py
import os
import asyncio
from fastapi import FastAPI, Body
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

from database import query

# Load environment variables
load_dotenv()

app = FastAPI()

model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
normalize = os.getenv("NORMALIZE_EMBEDDINGS", "true").lower() == "true"
host = os.getenv("EMBEDDING_HOST", "0.0.0.0")
port = int(os.getenv("EMBEDDING_PORT", "8000"))

model = SentenceTransformer(model_name)

@app.on_event("startup")
async def startup_event():
    question = "I am scared"
    print(f"Generating embedding for sample question: '{question}'")
    embedding = model.encode([question], normalize_embeddings=normalize)
    vector_str = "[" + ",".join(str(x) for x in embedding[0].tolist()) + "]"
    results = await query(
        """
        SELECT content
        FROM documents
        ORDER BY embedding <-> $1
        LIMIT $2;
        """,
        vector_str,  # or embedding[0].tolist() if using pgvector.register_vector
        5
    )
    print("Top 5 similar documents:")
    for record in results:
        print(f"Content: {record['content'][:50]}...")

@app.post("/embed")
async def embed(texts: list[str] = Body(...)):
    embeddings = model.encode(texts, normalize_embeddings=normalize)
    return {"embeddings": embeddings.tolist()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("serve:app", host=host, port=port, reload=False)
