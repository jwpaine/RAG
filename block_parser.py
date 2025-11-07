from database import execute, init_db
from embeddings import get_embedding
import asyncio

async def main():
    # Initialize DB connection once
    await init_db()

    file = "data/fables.txt"
    print(f"Processing file: {file}")

    # Load and clean data
    with open(file, "r", encoding="utf-8") as f:
        data = f.read()
        
        paragraphs = data.split("\n\n")
        # remove first 2 lines (header)
        paragraphs = paragraphs[2:]
        i = 1

        content = ""
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            # if starts with --:
            if para.startswith("--"):
                if content:
                    print(f"Processing fable {title}: {content[:10]}...")
                    embedding = await get_embedding(content)
                    vector_str = "[" + ",".join(map(str, embedding)) + "]"
                    await execute(
                        """
                        INSERT INTO fables (title, content, embedding)
                        VALUES ($1, $2, $3);
                        """,
                        title, content, vector_str
                    )
                    
                title = para[2:].strip()
                content = ""
                continue

            content += para + "\n\n"
            

            

if __name__ == "__main__":
    asyncio.run(main())