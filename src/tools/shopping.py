from fastmcp import FastMCP
from src.client import MealieClient


def register_shopping_tools(mcp: FastMCP, client: MealieClient):

    @mcp.tool()
    async def get_shopping_lists() -> dict:
        """Get all shopping lists."""
        return await client.get("/groups/shopping/lists")

    @mcp.tool()
    async def get_shopping_list(list_id: str) -> dict:
        """Get a shopping list by ID, including all items."""
        return await client.get(f"/groups/shopping/lists/{list_id}")

    @mcp.tool()
    async def create_shopping_list(name: str) -> dict:
        """Create a new shopping list."""
        return await client.post("/groups/shopping/lists", {"name": name})

    @mcp.tool()
    async def add_item_to_shopping_list(list_id: str, note: str, quantity: float = 1.0, unit: str | None = None) -> dict:
        """Add an item to a shopping list."""
        data: dict = {"shoppingListId": list_id, "note": note, "quantity": quantity}
        if unit:
            data["unit"] = unit
        return await client.post("/groups/shopping/items", data)

    @mcp.tool()
    async def delete_shopping_list(list_id: str) -> dict:
        """Delete a shopping list by ID."""
        return await client.delete(f"/groups/shopping/lists/{list_id}")
