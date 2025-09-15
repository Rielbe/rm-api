from datetime import datetime
from httpx import AsyncClient
from pydantic import BaseModel, RootModel


BASE_API = "https://rickandmortyapi.com/api"



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




async def get_data() -> list[dict]:
    """Makes a set of queries in order to get the result specified in the requirements

    Returns:
        list[dict]: List of results from the API
    """
    
    async with AsyncClient(timeout=10) as client:
        # First list all possible locations that are "Earth"
        earth_locations = await make_safe_query(client, BASE_API + "/location?name=Earth")
