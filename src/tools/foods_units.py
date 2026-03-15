from typing import Optional
from fastmcp import FastMCP
from src.client import MealieClient


def register_foods_units_tools(mcp: FastMCP, client: MealieClient):

    @mcp.tool()
    async def get_foods(
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 100,
    ) -> dict:
        """List foods in the Mealie database. Use search to filter by name.
        Always call this before create_food to avoid duplicates.
        Returns id, name, pluralName, aliases for each food."""
        params: dict = {"page": page, "perPage": per_page}
        if search is not None:
            params["search"] = search
        return await client.get("/foods", params=params)

    @mcp.tool()
    async def get_units(
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 100,
    ) -> dict:
        """List measurement units in the Mealie database. Use search to filter by name.
        Always call this before create_unit to avoid duplicates.
        Returns id, name, abbreviation, aliases for each unit."""
        params: dict = {"page": page, "perPage": per_page}
        if search is not None:
            params["search"] = search
        return await client.get("/units", params=params)

    @mcp.tool()
    async def create_food(
        name: str,
        plural_name: Optional[str] = None,
        description: Optional[str] = None,
        aliases: Optional[list] = None,
    ) -> dict:
        """Create a new food entry in the Mealie database.
        Call get_foods first to check for existing matches before creating.
        aliases is a plain list of strings e.g. ['boneless chicken thigh'].
        Returns the created food including its id (needed for recipe ingredients)."""
        body: dict = {"name": name}
        if plural_name is not None:
            body["pluralName"] = plural_name
        if description is not None:
            body["description"] = description
        if aliases:
            body["aliases"] = [{"name": a} for a in aliases]
        return await client.post("/foods", body)

    @mcp.tool()
    async def create_unit(
        name: str,
        plural_name: Optional[str] = None,
        abbreviation: Optional[str] = None,
        aliases: Optional[list] = None,
    ) -> dict:
        """Create a new measurement unit in the Mealie database.
        Call get_units first to check for existing matches before creating.
        aliases is a plain list of strings e.g. ['gram', 'grams'].
        Returns the created unit including its id (needed for recipe ingredients)."""
        body: dict = {"name": name}
        if plural_name is not None:
            body["pluralName"] = plural_name
        if abbreviation is not None:
            body["abbreviation"] = abbreviation
        if aliases:
            body["aliases"] = [{"name": a} for a in aliases]
        return await client.post("/units", body)
