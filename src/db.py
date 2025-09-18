import asyncpg
import json
from os import getenv
from typing import Any

DB_CONFIG = {
    "user": getenv("PG_USER"),
    "password": getenv("PG_PASSWORD"),
    "database": "rmapi",
    "host": getenv("PG_HOST"),
    "port": 5432,
}

DB_AVAILABLE = False

pool: asyncpg.pool.Pool | None = None

async def init_db():
    global pool
    global DB_AVAILABLE
    try:
        pool = await asyncpg.create_pool(**DB_CONFIG)
        async with pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS query(
                    id SERIAL PRIMARY KEY,
                    ts TIMESTAMP,
                    data JSON
                )
            ''')
        print("Database initialized successfully!")
        DB_AVAILABLE = True
    except Exception as e:
        print(f"Database connection failed: {e}")

async def close_db():
    global pool
    if pool:
        await pool.close()
        pool = None
        print("Database connection closed")


async def insert_query(data: Any):
    """
    Insert a Python object (dict/list) into the `query` table as JSON.
    """
    if not DB_AVAILABLE or pool is None:
        return 0

    # Convert Python object to JSON string
    json_data = json.dumps(data)

    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO query(ts, data)
            VALUES (NOW(), $1)
            """,
            json_data
        )