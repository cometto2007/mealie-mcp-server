from fastmcp import FastMCP
from src.client import MealieClient


def register_recipe_tools(mcp: FastMCP, client: MealieClient):

    @mcp.tool()
    async def search_recipes(query: str, page: int = 1, per_page: int = 10) -> dict:
        """Search for recipes by name or keyword."""
        return await client.get("/recipes", params={"search": query, "page": page, "perPage": per_page})

    @mcp.tool()
    async def get_recipe(slug: str) -> dict:
        """Get full details for a recipe by its slug."""
        return await client.get(f"/recipes/{slug}")

    @mcp.tool()
    async def get_all_recipes(page: int = 1, per_page: int = 20) -> dict:
        """Get a paginated list of all recipes."""
        return await client.get("/recipes", params={"page": page, "perPage": per_page})

    @mcp.tool()
    async def create_recipe(name: str) -> dict:
        """Create a new recipe with a given name."""
        return await client.post("/recipes", {"name": name})

    @mcp.tool()
    async def delete_recipe(slug: str) -> dict:
        """Delete a recipe by its slug."""
        return await client.delete(f"/recipes/{slug}")
