import asyncio
from fastapi import FastAPI

from src.endpoints.get_character_data import character_router
from src.rm_api import get_data


app = FastAPI()
app.include_router(character_router)


if __name__ == "__main__":
    result = asyncio.run(get_data())
