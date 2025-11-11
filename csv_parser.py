from database import execute, init_db
from embeddings import get_embedding
import asyncio
import csv

NUM_CHUNKS = 8

# Columns before emotions begin
NON_EMOTION_COLUMNS = [
    "text", "id", "author", "subreddit", "link_id", "parent_id",
    "created_utc", "rater_id", "example_very_unclear"
]

async def process_chunk(chunk, chunk_id, total_chunks):
    """Process a subset of (label, text) emotion pairs concurrently."""
    for i, (label, text) in enumerate(chunk, start=1):
        embedding = await get_embedding(text)
        vector_str = "[" + ",".join(map(str, embedding)) + "]"

        # print label and first 60 chars of text for verification
        # print(f"label: {label}, text: {text[:60]}...")

        await execute(
            """
            INSERT INTO emotions (label, embedding)
            VALUES ($1, $2);
            """,
            label, vector_str
        )

        if i % 20 == 0:
            print(f"[Chunk {chunk_id}/{total_chunks}] Inserted {i} records.")

    print(f"[Chunk {chunk_id}/{total_chunks}] Done ({len(chunk)} records).")


async def main():
    await init_db()

    file = "data/emotions.csv"
    print(f"Processing file: {file}")

    labeled_pairs = []

    # --- Parse CSV safely ---
    with open(file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Derive emotion column names dynamically
        emotion_columns = [c for c in reader.fieldnames if c not in NON_EMOTION_COLUMNS]

        for row in reader:
            text = row.get("text", "").strip()
            if not text:
                continue

            # Each row can have multiple '1's (multi-label)
            for emotion in emotion_columns:
                if row.get(emotion, "0") == "1":
                    labeled_pairs.append((emotion, text))

    total = len(labeled_pairs)
    chunk_size = (total // NUM_CHUNKS) + 1
    chunks = [labeled_pairs[i:i + chunk_size] for i in range(0, total, chunk_size)]

    print(f"Split {total} (label, text) records into {len(chunks)} chunks.")

    tasks = [
        asyncio.create_task(process_chunk(chunk, i + 1, len(chunks)))
        for i, chunk in enumerate(chunks)
    ]
    await asyncio.gather(*tasks)
    print("🎉 All chunks processed successfully.")


if __name__ == "__main__":
    asyncio.run(main())
