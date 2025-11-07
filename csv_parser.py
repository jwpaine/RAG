from database import execute, init_db
from embeddings import get_embedding
import asyncio

NUM_CHUNKS = 8

async def process_chunk(chunk, chunk_id, total_chunks):
    for i, (english, spanish) in enumerate(chunk, start=1):
        embedding = await get_embedding(spanish)
        vector_str = "[" + ",".join(map(str, embedding)) + "]"
        await execute(
            """
            INSERT INTO documents (english, spanish, embedding)
            VALUES ($1, $2, $3);
            """,
            english, spanish, vector_str
        )
        if i % 20 == 0:
            print(f"[Chunk {chunk_id}/{total_chunks}] Inserted {i} records.")

    print(f"[Chunk {chunk_id}/{total_chunks}] Done ({len(chunk)} records)")


async def main():
    # Initialize DB connection once
    await init_db()

    file = "data/introductions.csv"
    print(f"Processing file: {file}")

    # Load and clean data
    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()[1:]  # skip header

    pairs = []
    for line in lines:
        parts = line.strip().split(",")
        if len(parts) >= 2:
            english, spanish = parts[0].strip(), parts[1].strip()
            pairs.append((english, spanish))

    total = len(pairs)
    chunk_size = (total // NUM_CHUNKS) + 1
    chunks = [pairs[i:i + chunk_size] for i in range(0, total, chunk_size)]

    print(f"Split {total} records into {len(chunks)} chunks.")

    # Process chunks concurrently (share the same DB connection)
    tasks = [
        asyncio.create_task(process_chunk(chunk, i + 1, len(chunks)))
        for i, chunk in enumerate(chunks)
    ]

    await asyncio.gather(*tasks)
    print("All chunks processed successfully.")


if __name__ == "__main__":
    asyncio.run(main())
