import sqlite3

from agents import function_tool
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / 'data'
DB_FILE = DATA_DIR / 'AllPrintings.sqlite'

COLOR_NAMES = {'W': 'White', 'U': 'Blue', 'B': 'Black', 'R': 'Red', 'G': 'Green'}
FORMATS = ('standard', 'pioneer', 'modern', 'legacy', 'vintage', 'pauper', 'commander')

def _color_names(codes: str | None) -> list[str]:
    names = [COLOR_NAMES[c.strip()] for c in (codes or '').split(',') if c.strip()]
    return names or ['Colorless']

@function_tool
def get_card(name: str) -> dict:
    """Look up a single Magic: The Gathering Card by name.

    Use this tool when a user asks about a card by name. Returns the mana cost, type,
    card text, colors, colorIdentity, power (if applicable), toughness (if applicable),
    and legalities.

    Args:
        name: Card name. Partial names are acceptable as well as any type of capitalization.
    """
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row

        row = conn.execute(
            f"""
            SELECT c.name, c.manaCost, c.type, c.text, c.colors, c.colorIdentity,
                   c.power, c.toughness, {', '.join(f'l.{f}' for f in FORMATS)}
            FROM cards c
            LEFT JOIN cardLegalities l ON l.uuid = c.uuid
            WHERE c.name = ? COLLATE NOCASE
            LIMIT 1
            """,
            (name,)
        ).fetchone()

        if row:
            card = {k: row[k] for k in row.keys() if k not in FORMATS}
            card['colors'] = _color_names(card['colors'])
            card['colorIdentity'] = _color_names(card['colorIdentity'])
            card['legalities'] = {f: row[f] or 'Not legal' for f in FORMATS}
            return {"found": True, **card}

        like = conn.execute(
            """
            SELECT DISTINCT name FROM cards WHERE name LIKE ? LIMIT 5
            """,
            (f'%{name}%',)
        ).fetchall()

        if like:
            return {"found": False, "suggestions": [r['name'] for r in like]}
        else:
            return {"found": False, "error": 'No cards exist with this name'}
