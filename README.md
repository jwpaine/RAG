I used all-MiniLM-L6-v2 — which maps the meaning of the text to a point in 384-dimensional space.

I added 100 Yoda quotes to a CSV file and wrote a script to calculate their vectors.

All quotes, along with their vectors, were added to postgres.

I took the question: “What’s the answer to life, the universe, and everything?”, 
passed it through the embedding model to get its 384-dimensional vector,
and asked Postgres to return the quote whose vector was closest:

Requesting embedding for text: What's the answer to life, the universe and everything?
Embedding vector length: 384
First 8 dimensions: [-0.0636 -0.0009 -0.0438 0.0429 0.0014 0.0388 -0.0077 -0.0091]
Similar: [The galaxy, full of lessons it is.]

Thank you, Yoda!



