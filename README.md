
Everyone’s talking about how to use AI to generate code,
but no one on my feed ever talks about organizing what they already know.

This weekend I had some fun playing around with a tiny embeddings model: all-MiniLM-L6-v2. 
Text goes in, and instead of language coming out, you get a vector which represents the meaning of that text. A single point in
higher dimensional space. I spun up an app where I could submit a string of text, and get back it's semantic position. 

I used it to calculate the position of 100 Yoda quotes:

"Fear is the path to the dark side". The meaning of this quote mapped to [0.060235,0.017227,-0.001324,0.151363, ...]
"Always pass on what you have learned" Mapped to [0.054547,0.016146,-0.013533,0.015499, ...]

All of these were added to a PostgreSQL database with the pgvector extension.

I came up with a question, passed it through the same embedding model, and then asked the database to return the quote who's vector was the closest distance from the one my question mapped to:

Requesting embedding for text: What's the answer to life, the universe and everything? 
...Embedding vector length: 384, First 8 dimensions: [-0.0636 -0.0009 -0.0438 0.0429 0.0014 0.0388 -0.0077 -0.0091]
Most Similar: "Galaxy, full of lessons it is."

Thank you, Yoda!

We're two months out from what may be the greatest year for AI, and the ones with searchable knowledge bases will be able to pivot faster than the rest.




python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install fastapi uvicorn sentence-transformers python-dotenv asyncpg
