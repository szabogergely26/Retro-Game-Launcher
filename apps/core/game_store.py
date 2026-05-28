"""
Retro Game Launcher - játékadatok tárolása

Ez a modul kezeli a launcher saját játéklistáját.
Első körben egyszerű JSON fájlba mentünk, mert ehhez a projekthez most bőven elég.
"""

import json
from pathlib import Path


# A felhasználó saját app-adat könyvtára.
APP_DATA_DIR = Path.home() / ".local" / "share" / "retro-game-launcher"

# Ebben lesznek a felvett játékok.
GAMES_FILE = APP_DATA_DIR / "games.json"


def load_games() -> list[dict]:
    """
    Betölti a felvett játékokat.

    Ha még nincs games.json, akkor üres listát ad vissza.
    Ha a fájl sérült vagy nem lista van benne, szintén üres listát ad vissza.
    """

    if not GAMES_FILE.exists():
        return []

    try:
        content = GAMES_FILE.read_text(encoding="utf-8")
        data = json.loads(content)

    except (OSError, json.JSONDecodeError):
        return []

    if not isinstance(data, list):
        return []

    return data


def save_games(games: list[dict]) -> None:
    """
    Elmenti a teljes játéklistát.
    """

    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

    content = json.dumps(games, ensure_ascii=False, indent=4)
    GAMES_FILE.write_text(content, encoding="utf-8")


def add_game(game: dict) -> None:
    """
    Hozzáad egy játékot a játéklistához.
    """

    games = load_games()
    games.append(game)
    save_games(games)


def delete_game_by_index(index: int) -> None:
    """
    Töröl egy játékot a játéklistából listaindex alapján.
    """

    games = load_games()

    if index < 0 or index >= len(games):
        return

    del games[index]
    save_games(games)



# Import / Export funkció (Játéklista Mentése / Betöltése):

def export_games_to_file(target_path: str | Path) -> None:
    """
    Exportálja a jelenlegi játéklistát egy kiválasztott JSON fájlba.
    """

    games = load_games()

    target_file = Path(target_path)
    target_file.parent.mkdir(parents=True, exist_ok=True)

    content = json.dumps(games, ensure_ascii=False, indent=4)
    target_file.write_text(content, encoding="utf-8")


def import_games_from_file(source_path: str | Path) -> None:
    """
    Importál egy játéklistát egy kiválasztott JSON fájlból,
    majd elmenti az alkalmazás saját games.json fájljába.
    """

    source_file = Path(source_path)

    content = source_file.read_text(encoding="utf-8")
    data = json.loads(content)

    if not isinstance(data, list):
        raise ValueError("A kiválasztott fájl nem érvényes játéklista.")

    save_games(data)
