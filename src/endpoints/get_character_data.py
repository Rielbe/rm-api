from fastapi import APIRouter, Query
from operator import attrgetter

from src.rm_api import Character_Data, get_data


character_router = APIRouter()

@character_router.get("/earth_characters")
async def get_earth_characters(sort_by: list[str] | None = Query(None, description=f"Allowed values: {', '.join(list(Character_Data.model_fields.keys()))}")) -> list[Character_Data]:
    
    earth_characters = await get_data()

    if not sort_by:
        return earth_characters
    
    for field in sort_by:
        if field not in Character_Data.model_fields:
            raise ValueError(f"Invalid sort field: {field}")
    
    sorted_characters = sorted(
        earth_characters,
        key=attrgetter(*sort_by)
    )

    return sorted_characters