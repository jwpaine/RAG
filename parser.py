from database import query, execute
from embeddings import get_embedding
import re
import asyncio


def chunk_text(text, max_chars=800, overlap=100):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = ""

    for s in sentences:
        if len(current) + len(s) + 1 <= max_chars:
            current += " " + s
        else:
            # save the chunk
            chunks.append(current.strip())

            # build the next chunk with overlap from previous
            if overlap:
                overlap_start = current[-overlap:].split(" ", 1)[-1]  # avoid cutting in middle of word
                current = overlap_start + " " + s
            else:
                current = s

    if current.strip():
        chunks.append(current.strip())

    return chunks


async def main():
    # read file
    with open("data/meditations.txt", "r") as f:
        content = f.read()
        # split into paragraphs
        paragraphs = content.split("\n\n")

        book = ""
        p = 1
        for para in paragraphs:
            if para.strip() == "":
                continue
            if "B_" in para:
                book = para
                p = 1
                continue
            # remove paragraph numbers
            para = para[para.find(".")+2:]

            chunks = chunk_text(para, max_chars=800, overlap=100)
            print(f"Processing {book}_p_{p} with {len(chunks)} chunks.")
            title = f"{book}_P_{p}"
            for c in chunks:
                embedding = await get_embedding("sentence-transformers/all-MiniLM-L6-v2", c)
                vector_str = "[" + ",".join(map(str, embedding)) + "]"
                await execute(
                    """
                    INSERT INTO documents (content, embedding, title)
                    VALUES ($1, $2, $3);
                    """,
                    c, vector_str, title
                )
                print(f"Chunk embedded and stored.")

            p+=1

if __name__ == "__main__":
    asyncio.run(main())



            