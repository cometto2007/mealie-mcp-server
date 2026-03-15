from typing import Optional
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

    @mcp.tool()
    async def update_recipe(
        slug: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        recipe_servings: Optional[float] = None,
        total_time: Optional[str] = None,
        prep_time: Optional[str] = None,
        perform_time: Optional[str] = None,
        org_url: Optional[str] = None,
        calories: Optional[str] = None,
        protein_content: Optional[str] = None,
        carbohydrate_content: Optional[str] = None,
        fat_content: Optional[str] = None,
        fiber_content: Optional[str] = None,
        sodium_content: Optional[str] = None,
        sugar_content: Optional[str] = None,
        cholesterol_content: Optional[str] = None,
        saturated_fat_content: Optional[str] = None,
        recipe_ingredient: Optional[list] = None,
        recipe_instructions: Optional[list] = None,
        show_nutrition: Optional[bool] = None,
        public: Optional[bool] = None,
        show_assets: Optional[bool] = None,
        landscape_view: Optional[bool] = None,
        disable_comments: Optional[bool] = None,
        locked: Optional[bool] = None,
    ) -> dict:
        """Partially update a recipe. Only provided fields are sent.
        Nutrition values are per-serving strings (e.g. calories='540').
        recipe_ingredient items must use food/unit objects with id fields.
        recipe_instructions items must have a 'text' field.
        Settings fields control recipe display: show_nutrition, public, show_assets, landscape_view, disable_comments, locked."""
        body: dict = {}

        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if recipe_servings is not None:
            body["recipeServings"] = recipe_servings
        if total_time is not None:
            body["totalTime"] = total_time
        if prep_time is not None:
            body["prepTime"] = prep_time
        if perform_time is not None:
            body["performTime"] = perform_time
        if org_url is not None:
            body["orgURL"] = org_url
        if recipe_ingredient is not None:
            body["recipeIngredient"] = recipe_ingredient
        if recipe_instructions is not None:
            body["recipeInstructions"] = recipe_instructions

        nutrition_map = {
            "calories": calories,
            "proteinContent": protein_content,
            "carbohydrateContent": carbohydrate_content,
            "fatContent": fat_content,
            "fiberContent": fiber_content,
            "sodiumContent": sodium_content,
            "sugarContent": sugar_content,
            "cholesterolContent": cholesterol_content,
            "saturatedFatContent": saturated_fat_content,
        }
        nutrition = {k: v for k, v in nutrition_map.items() if v is not None}
        if nutrition:
            body["nutrition"] = nutrition

        settings_map = {
            "showNutrition": show_nutrition,
            "public": public,
            "showAssets": show_assets,
            "landscapeView": landscape_view,
            "disableComments": disable_comments,
            "locked": locked,
        }
        settings = {k: v for k, v in settings_map.items() if v is not None}
        if settings:
            body["settings"] = settings

        return await client.patch(f"/recipes/{slug}", body)

    @mcp.tool()
    async def import_recipe_url(url: str, include_tags: bool = False) -> dict:
        """Import a recipe from a URL using Mealie's built-in scraper.
        Returns the slug of the created recipe."""
        return await client.post("/recipes/create/url", {"url": url, "includeTags": include_tags})

    @mcp.tool()
    async def parse_ingredients(ingredients: list, parser: str = "nlp") -> dict:
        """Parse free-text ingredient strings into structured food/unit/quantity objects.
        parser can be 'nlp' (default, English) or 'brute'.
        Example: ingredients=['200g chicken thigh', '2 tbsp soy sauce']"""
        return await client.post("/parser/ingredients", {"parser": parser, "ingredients": ingredients})
