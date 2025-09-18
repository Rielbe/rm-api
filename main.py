import asyncio
from fastapi import FastAPI

from src.endpoints.get_character_data import character_router
from src.db import init_db, close_db
from src.rm_api import get_data

async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()

app = FastAPI(lifespan=lifespan)
app.include_router(character_router)


if __name__ == "__main__":
    result = asyncio.run(get_data())
