from database import query, execute
from embeddings import get_embedding

# read file
with open("data/meditations.txt", "r") as f:
    content = f.read()
    # split into paragraphs
    paragraphs = content.split("\n\n")
    # print first 4 words of each paragraph
    # for word in paragraphs:
    #     print(word[:40])
    book = ""
    for para in paragraphs:
        if para.strip() == "":
            continue
        if "BOOK_" in para:
            book = para
            continue
        # get index of first period
        i = para.find(".")
        para_number = para[:i]
        print(f"{book}_{para_number}")
            