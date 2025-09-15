from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
from operator import attrgetter

from src.rm_api import Character_Data, get_data

class ErrorResponse(BaseModel):
    detail: str

character_router = APIRouter()

@character_router.get("/earth_characters", responses={
    400: {
        "model": ErrorResponse,
        "description": "Invalid user input"
    }
})
async def get_earth_characters(sort_by: list[str] | None = Query(None, description=f"Allowed values: {', '.join(list(Character_Data.model_fields.keys()))}")) -> list[Character_Data]:
    
    earth_characters = await get_data()

    if not sort_by:
        return earth_characters
    
    for field in sort_by:
        if field not in Character_Data.model_fields:
            raise HTTPException(detail=f"Invalid sort field: {field}", status_code=status.HTTP_400_BAD_REQUEST)
    
    sorted_characters = sorted(
        earth_characters,
        key=attrgetter(*sort_by)
    )

    return sorted_characters