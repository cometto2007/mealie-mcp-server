import json
import os
import sys
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

    def _log(self, method: str, path: str, body: Any = None) -> None:
        msg = f"[mealie] {method} /api{path}"
        if body is not None:
            msg += f"\n  payload: {json.dumps(body, indent=2)}"
        print(msg, file=sys.stderr, flush=True)

    def _raise_with_body(self, response: httpx.Response) -> None:
        """Raise an exception that includes the Mealie error response body."""
        try:
            detail = response.json()
        except Exception:
            detail = response.text
        raise httpx.HTTPStatusError(
            f"Mealie API error {response.status_code}: {json.dumps(detail)}",
            request=response.request,
            response=response,
        )

    async def get(self, path: str, params: dict | None = None) -> Any:
        self._log("GET", path)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api{path}",
                headers=self.headers,
                params=params,
            )
            if response.is_error:
                self._raise_with_body(response)
            return response.json()

    async def post(self, path: str, data: dict) -> Any:
        self._log("POST", path, data)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api{path}",
                headers=self.headers,
                json=data,
            )
            if response.is_error:
                self._raise_with_body(response)
            return response.json()

    async def put(self, path: str, data: dict) -> Any:
        self._log("PUT", path, data)
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}/api{path}",
                headers=self.headers,
                json=data,
            )
            if response.is_error:
                self._raise_with_body(response)
            return response.json()

    async def patch(self, path: str, data: dict) -> Any:
        self._log("PATCH", path, data)
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/api{path}",
                headers=self.headers,
                json=data,
            )
            if response.is_error:
                self._raise_with_body(response)
            return response.json()

    async def delete(self, path: str) -> Any:
        self._log("DELETE", path)
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/api{path}",
                headers=self.headers,
            )
            if response.is_error:
                self._raise_with_body(response)
            return response.json()
