import asyncio
from datetime import datetime
from httpx import AsyncClient
from pydantic import BaseModel
from typing import Literal

BASE_API = "https://rickandmortyapi.com/api"

class API_Metadata(BaseModel):
    count: int
    pages: int
    next: str | None
    prev: str | None

class LocationFilter(BaseModel):
    name: str
    url: str

class Character_Data(BaseModel):
    id: int
    name: str
    species: str
    type: str
    gender: str
    origin: LocationFilter
    location: LocationFilter
    image: str
    episode: list[str]
    url: str
    created: datetime

class Location_Data(BaseModel):
    id: int
    name: str
    type: str
    dimension: str
    residents: list[str]
    url: str
    created: datetime


class Character_Response(BaseModel):
    info: API_Metadata
    results: list[Character_Data]

class Location_Response(BaseModel):
    info: API_Metadata
    results: list[Location_Data]

Query_Type = Literal["character", "location"]

async def make_safe_query(client: AsyncClient, url: str) -> dict:
    """Method for handling errors

    Args:
        client (AsyncClient): Async client instance
        url (str): URL that contains all the parameters for the query

    Returns:
        dict: Result from the API
    """
    result = (await client.get(url)).json()
    return result

def parse_result(result: dict, type: Query_Type) -> Character_Response | Location_Response:
    if type == "character":
        return Character_Response(**result)
    elif type == "location":
        return Location_Response(**result)


async def get_paginated_results(client: AsyncClient, url: str, type: Query_Type) -> list[Character_Data | Location_Data]:
    """Method that resolves the pagination from the queries

    Args:
        client (AsyncClient): Async client instance
        url (str): URl that contains all the parameters for the query

    Returns:
        dict: Chained results from API
    """
    first_result = parse_result((await make_safe_query(client, url)), type)
    if first_result.info.next is None:
        return first_result.results
    
    queries = [url + f"&page={x}" for x in range(2, first_result.info.pages+1)]
    tasks = [make_safe_query(client, q) for q in queries]

    results = await asyncio.gather(*tasks)

    parsed_results = [parse_result(r, type) for r in results]

    return first_result.results + [r for sublist in parsed_results for r in sublist.results]


async def get_data() -> list[dict]:
    """Makes a set of queries in order to get the result specified in the requirements

    Returns:
        list[dict]: List of results from the API
    """
    
    async with AsyncClient(timeout=10) as client:
        # First list all possible locations that are "Earth"
        earth_locations = await get_paginated_results(client, BASE_API + "/location?name=Earth", "location")
        
