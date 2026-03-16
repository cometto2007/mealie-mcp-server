"""Fix NULL reference_id values on recipe ingredients.

Usage:
  docker cp scripts/fix_reference_ids.py mealiev1:/tmp/fix.py
  docker exec mealiev1 python3 /tmp/fix.py green-noodles
"""
import sqlite3
import sys
import uuid

slug = sys.argv[1] if len(sys.argv) > 1 else "green-noodles"
conn = sqlite3.connect("/app/data/mealie.db")
cur = conn.cursor()
cur.execute(
    "SELECT id FROM recipes_ingredients"
    " WHERE recipe_id=(SELECT id FROM recipes WHERE slug=?)"
    " AND reference_id IS NULL",
    (slug,),
)
rows = cur.fetchall()
print(f"{len(rows)} ingredients to fix for '{slug}'")
for r in rows:
    cur.execute(
        "UPDATE recipes_ingredients SET reference_id=? WHERE id=?",
        (str(uuid.uuid4()), r[0]),
    )
conn.commit()
conn.close()
print("Done")
