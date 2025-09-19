import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import time
from collections import defaultdict

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

RATE = 5  # max_requests
PER = 60  # refill window seconds

app = FastAPI(lifespan=lifespan)
app.include_router(character_router)


buckets = defaultdict(lambda: {"available_requests": RATE, "last": time.time()})

lock = asyncio.Lock()

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    key = request.client.host
    now = time.time()
    async with lock:
        bucket = buckets[key]
        elapsed = now - bucket["last"]
        refill = elapsed * (RATE / PER)
        bucket["available_requests"] = min(RATE, bucket["available_requests"] + refill)
        bucket["last"] = now

        if bucket["available_requests"] < 1:
            retry_after = int((1 - bucket["available_requests"]) * (PER / RATE))
            return JSONResponse(
                status_code=429,
                content={"detail": "Too Many Requests"},
                headers={"Retry-After": str(retry_after)}
            )
        else:
            bucket["available_requests"] -= 1

    response = await call_next(request)
    return response



if __name__ == "__main__":
    result = asyncio.run(get_data())
