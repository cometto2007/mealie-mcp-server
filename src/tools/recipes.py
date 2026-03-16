import uuid
from typing import Optional
from fastmcp import FastMCP
from src.client import MealieClient


async def _resolve_ingredient(ingredient: dict, client: MealieClient) -> dict:
    """Resolve a caller-supplied ingredient into a complete Mealie ingredient object.

    Accepts either:
    - Simplified:  {"quantity": N, "unit_id": "uuid", "food_id": "uuid", "note": "..."}
    - Passthrough: full Mealie ingredient dict copied from a GET response

    For simplified format, fetches the full food/unit objects from the Mealie API so
    the PUT body contains the same structure Mealie produced — avoiding the internal
    ValidationError that occurs when partial food/unit objects are round-tripped through
    Mealie's SQLAlchemy layer.
    """
    result: dict = {}

    # Resolve food — fetch full object when only id is known
    if "food_id" in ingredient:
        result["food"] = await client.get(f"/foods/{ingredient['food_id']}")
    elif "food" in ingredient and isinstance(ingredient["food"], dict):
        food = ingredient["food"]
        food_id = food.get("id")
        if food_id and "createdAt" not in food:
            # Partial object (e.g. {id, name}) — fetch full object from API
            result["food"] = await client.get(f"/foods/{food_id}")
        else:
            result["food"] = food  # already a full passthrough object
    else:
        result["food"] = None

    # Resolve unit — same pattern
    if "unit_id" in ingredient:
        result["unit"] = await client.get(f"/units/{ingredient['unit_id']}")
    elif "unit" in ingredient and isinstance(ingredient["unit"], dict):
        unit = ingredient["unit"]
        unit_id = unit.get("id")
        if unit_id and "createdAt" not in unit:
            result["unit"] = await client.get(f"/units/{unit_id}")
        else:
            result["unit"] = unit
    else:
        result["unit"] = None

    result["quantity"] = ingredient.get("quantity")
    result["note"] = ingredient.get("note", "")
    result["title"] = ingredient.get("title", "")
    result["display"] = ingredient.get("display", "")
    result["originalText"] = ingredient.get("originalText", None)
    result["referencedRecipe"] = ingredient.get("referencedRecipe", None)
    # Preserve existing referenceId so Mealie keeps ingredient identity; mint new UUID otherwise
    result["referenceId"] = ingredient.get("referenceId") or str(uuid.uuid4())

    return result


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

        recipe_ingredient: when provided, the tool fetches the full recipe via GET and
          replaces recipeIngredient with PUT (mirrors what the Mealie frontend does).
          Each item accepts either:
            - Simplified: {"quantity": N, "unit_id": "uuid", "food_id": "uuid", "note": ""}
            - Passthrough: full ingredient object copied from a get_recipe response
          Pass ALL ingredients (unchanged ones too) — Mealie replaces the entire array.

        recipe_instructions items must have a 'text' field.
        Settings fields: show_nutrition, public, show_assets, landscape_view,
          disable_comments, locked.
        """
        # Build the partial-update dict for non-ingredient fields (used for PATCH)
        patch_body: dict = {}

        if name is not None:
            patch_body["name"] = name
        if description is not None:
            patch_body["description"] = description
        if recipe_servings is not None:
            patch_body["recipeServings"] = recipe_servings
        if total_time is not None:
            patch_body["totalTime"] = total_time
        if prep_time is not None:
            patch_body["prepTime"] = prep_time
        if perform_time is not None:
            patch_body["performTime"] = perform_time
        if org_url is not None:
            patch_body["orgURL"] = org_url
        if recipe_instructions is not None:
            patch_body["recipeInstructions"] = recipe_instructions

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
            patch_body["nutrition"] = nutrition

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
            patch_body["settings"] = settings

        if recipe_ingredient is not None:
            # GET the full recipe, resolve ingredient food/unit to complete objects,
            # apply any other pending field changes, then PUT the whole thing back.
            # This mirrors what the Mealie frontend does and avoids the internal
            # ValidationError that Mealie throws when partial food/unit objects are
            # passed through PATCH's internal GET→merge→update cycle.
            full_recipe = await client.get(f"/recipes/{slug}")

            resolved = [await _resolve_ingredient(i, client) for i in recipe_ingredient]
            full_recipe["recipeIngredient"] = resolved

            # Overlay any other field changes onto the full recipe
            full_recipe.update(patch_body)

            return await client.put(f"/recipes/{slug}", full_recipe)

        if patch_body:
            return await client.patch(f"/recipes/{slug}", patch_body)

        return {"message": "No fields provided — nothing updated."}

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
