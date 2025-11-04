from sentence_transformers import SentenceTransformer
import asyncio


"""Generate a normalized embedding for the given text."""
async def get_embedding(model, text: str) -> list[float]:
    model = SentenceTransformer(model)
    #print(f"Generating embedding for text: '{text}'")
    embedding = await asyncio.to_thread(lambda: model.encode(text, normalize_embeddings=True))
    return embedding.tolist()