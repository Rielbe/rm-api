from fastapi import APIRouter, HTTPException, status, Query, Request
from pydantic import BaseModel
from operator import attrgetter

from src.rm_api import Character_Data, get_data

from src.cache import cache_available, cache_is_ready
from src.db import db_available

class ErrorResponse(BaseModel):
    detail: str

character_router = APIRouter()

@character_router.get("/earth_characters", responses={
    400: {
        "model": ErrorResponse,
        "description": "Invalid user input"
    }
})
async def get_earth_characters(request: Request, sort_by: list[str] | None = Query(None, description=f"Allowed values: {', '.join(list(Character_Data.model_fields.keys()))}")) -> list[Character_Data]:
    if sort_by:
        for field in sort_by:
            if field not in Character_Data.model_fields:
                raise HTTPException(detail=f"Invalid sort field: {field}", status_code=status.HTTP_400_BAD_REQUEST)

    allowed_params = {"sort_by"}
    for param in request.query_params.keys():
        if param not in allowed_params:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown query parameter: {param}"
            )

    earth_characters = await get_data()

    if not sort_by:
        return earth_characters
    sorted_characters = sorted(
        earth_characters,
        key=attrgetter(*sort_by)
    )

    return sorted_characters

# Using same router for simplicity
@character_router.get("/healthcheck")
async def get_status():
    return {"Server cache available": cache_available(), "Cache is ready": await cache_is_ready(), "DB available": db_available()}