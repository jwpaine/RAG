# database/pg.py
import asyncpg, os

_pool = None

async def get_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            host=os.getenv("PG_HOST", "localhost"),
            port=os.getenv("PG_PORT", "54321"),
            database=os.getenv("PG_DB", "vectordb"),
            user=os.getenv("PG_USER", "postgres"),
            password=os.getenv("PG_PASSWORD", "postgres"),
            min_size=1,
            max_size=5
        )
    return _pool

async def query(query, *args):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch(query, *args)

async def execute(query, *args):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.execute(query, *args)
    
async def init_db():
    print("Initializing database...")
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE EXTENSION IF NOT EXISTS vector;
                            
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                english TEXT NOT NULL,
                spanish TEXT NOT NULL,
                embedding VECTOR(384), -- all-MiniLM-L6-v2 embedding size
                metadata JSONB DEFAULT '{}'::jsonb
            );
        """)



        

   
