import os
from fastapi import FastAPI, Body
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
normalize = os.getenv("NORMALIZE_EMBEDDINGS", "true").lower() == "true"
host = os.getenv("EMBEDDING_HOST", "0.0.0.0")
port = int(os.getenv("EMBEDDING_PORT", "8000"))

print(f"Loading model: {model_name}")
model = SentenceTransformer(model_name)

@app.post("/embed")
async def embed(texts: list[str] = Body(...)):
    embeddings = model.encode(texts, normalize_embeddings=normalize)
    return {"embeddings": embeddings.tolist()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("embed_server:app", host=host, port=port, reload=False)
