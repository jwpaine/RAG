from sentence_transformers import SentenceTransformer
import asyncio

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
model = SentenceTransformer(MODEL_NAME)

"""Generate a normalized embedding for the given text."""
async def get_embedding(text: str) -> list[float]:
    #print(f"Generating embedding for text: '{text}'")
    embedding = await asyncio.to_thread(lambda: model.encode(text, normalize_embeddings=True))
    return embedding.tolist()