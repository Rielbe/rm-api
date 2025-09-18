import asyncio
from datetime import datetime
from fastapi import HTTPException
from httpx import AsyncClient
import json
from pydantic import BaseModel
from typing import Literal

from src.cache import insert_redis, get_redis
from src.db import insert_query

BASE_API = "https://rickandmortyapi.com/api"

class API_Metadata(BaseModel):
    count: int
    pages: int
    next: str | None
    prev: str | None

class LocationFilter(BaseModel):
    name: str
    url: str

    def __eq__(self, other):
        if isinstance(other, LocationFilter):
            return self.name == other.name
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, LocationFilter):
            return self.name < other.name
        return NotImplemented


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

MAX_TRIES = 10

async def make_safe_query(client: AsyncClient, url: str) -> dict:
    """Method for handling errors

    Args:
        client (AsyncClient): Async client instance
        url (str): URL that contains all the parameters for the query

    Returns:
        dict: Result from the API
    """
    tries = 0
    while True:
        if tries >= MAX_TRIES:
            raise HTTPException(500, "API server may not be available. Max retries reached...")
        try:
            response = await client.get(url)
            response.raise_for_status()
            result = response.json()
            break
        except Exception as e:
            print("Error while making query, trying again...")
            print(e)
            tries += 1
            asyncio.sleep(1)
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


async def get_data() -> list[Character_Data]:
    """Makes a set of queries in order to get the result specified in the requirements

    Returns:
        list[dict]: List of results from the API
    """

    try:
        raw_data = await get_redis("DATA")
        if raw_data is not None:
            data = json.loads(raw_data)
            data = [Character_Data.model_validate_json(entry) for entry in data]
            return data
    except Exception as e:
        print("Something went wrong with reading redis data. Querying again agains API...")
        print(e)

    async with AsyncClient(timeout=10) as client:
        # First list all possible locations that are "Earth"
        earth_locations = await get_paginated_results(client, BASE_API + "/location?name=Earth", "location")
        earth_fixed_names = [x.name for x in earth_locations]
        
        characters = await get_paginated_results(client, BASE_API + "/character?species=human&status=alive", "character")
        earth_characters = [x for x in characters if x.origin.name in earth_fixed_names]

        json_serialized_data = [x.model_dump_json() for x in earth_characters]
        try:
            await insert_redis("DATA", json_serialized_data)
        except Exception as e:
            print("~UPS! Something wrong with Redis insert!")
            print(e)
        try:
            await insert_query(json_serialized_data)
        except Exception as e:
            print("~UPS! Something wrong with DB insert!")
            print(e)
        return earth_characters