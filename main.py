import asyncio
from fastapi import FastAPI

from src.endpoints.get_character_data import character_router
from src.cache import init_redis, close_redis
from src.db import init_db, close_db
from src.rm_api import get_data

async def lifespan(app: FastAPI):
    await init_db()
    await init_redis()
    yield
    await close_redis()
    await close_db()

app = FastAPI(lifespan=lifespan)
app.include_router(character_router)


if __name__ == "__main__":
    result = asyncio.run(get_data())
