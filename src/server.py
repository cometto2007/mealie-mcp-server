import os
from dotenv import load_dotenv
from fastmcp import FastMCP
from src.client import MealieClient
from src.tools.recipes import register_recipe_tools
from src.tools.mealplans import register_mealplan_tools
from src.tools.shopping import register_shopping_tools
from src.tools.foods_units import register_foods_units_tools

load_dotenv()

mcp = FastMCP("mealie-server")
client = MealieClient()

register_recipe_tools(mcp, client)
register_mealplan_tools(mcp, client)
register_shopping_tools(mcp, client)
register_foods_units_tools(mcp, client)

if __name__ == "__main__":
    transport = os.environ.get("MCP_TRANSPORT", "streamable-http")
    host = os.environ.get("MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_PORT", "8000"))

    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(transport="streamable-http", host=host, port=port, stateless_http=True)
