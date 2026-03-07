from fastmcp import FastMCP
from src.client import MealieClient


def register_mealplan_tools(mcp: FastMCP, client: MealieClient):

    @mcp.tool()
    async def get_meal_plans(start_date: str | None = None, end_date: str | None = None) -> dict:
        """Get meal plans, optionally filtered by date range (YYYY-MM-DD format)."""
        params = {}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return await client.get("/groups/mealplans", params=params or None)

    @mcp.tool()
    async def get_today_meal_plan() -> dict:
        """Get today's meal plan."""
        return await client.get("/groups/mealplans/today")

    @mcp.tool()
    async def create_meal_plan(date: str, recipe_id: str, entry_type: str = "dinner") -> dict:
        """Create a meal plan entry. entry_type can be breakfast, lunch, dinner, or side."""
        return await client.post("/groups/mealplans", {
            "date": date,
            "recipeId": recipe_id,
            "entryType": entry_type,
        })

    @mcp.tool()
    async def delete_meal_plan(plan_id: int) -> dict:
        """Delete a meal plan entry by ID."""
        return await client.delete(f"/groups/mealplans/{plan_id}")
