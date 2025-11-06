from database import query, execute, init_db
from embeddings import get_embedding
import re
import asyncio

MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

async def main():
    await init_db()
    file = "data/translations.csv"
    print(f"Processing file: {file}")
    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        l = len(lines)
        c = 1
        for line in lines[1:]:  # Skip header
            parts = line.strip().split(",")
            if len(parts) < 2:
                continue
            english = parts[0].strip()
            spanish = parts[1].strip()

            embedding = await get_embedding(MODEL, spanish)
            vector_str = "[" + ",".join(map(str, embedding)) + "]"
            await execute(
                """
                INSERT INTO documents (english, spanish, embedding)
                VALUES ($1, $2, $3);
                """,
                english, spanish, vector_str
            )
            c += 1
            if c % 20 == 0 or c == l:
                print(f"Inserted {c}/{l} records.")
   

if __name__ == "__main__":
    asyncio.run(main())



            