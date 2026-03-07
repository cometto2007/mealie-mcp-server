import os
import httpx
from typing import Any


class MealieClient:
    def __init__(self):
        self.base_url = os.environ["MEALIE_URL"].rstrip("/")
        self.api_token = os.environ["MEALIE_API_TOKEN"]
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    async def get(self, path: str, params: dict | None = None) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api{path}",
                headers=self.headers,
                params=params,
            )
            response.raise_for_status()
            return response.json()

    async def post(self, path: str, data: dict) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api{path}",
                headers=self.headers,
                json=data,
            )
            response.raise_for_status()
            return response.json()

    async def put(self, path: str, data: dict) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}/api{path}",
                headers=self.headers,
                json=data,
            )
            response.raise_for_status()
            return response.json()

    async def delete(self, path: str) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/api{path}",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()
