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



def delete_game_by_desktop_path(desktop_path: str) -> None:
    """
    Töröl egy játékot a játéklistából a desktop_path alapján.
    """

    games = load_games()

    filtered_games = [
        game for game in games
        if game.get("desktop_path", "") != desktop_path
    ]

    save_games(filtered_games)
