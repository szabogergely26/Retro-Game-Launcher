"""
Retro Game Launcher - Wine alapbeállítások Windows-os játékokhoz

Ez a modul felelős azért, hogy amikor felveszel egy Windows-os (.exe)
játékot, a Wine automatikusan be legyen állítva hozzá - nem kell
kézzel babrálni a Wine beállításait minden egyes játéknál.
"""

import os
import subprocess
from pathlib import Path

from apps.core.game_store import APP_DATA_DIR
from apps.core.logger import get_logger


logger = get_logger(__name__)


# --- Ide írhatod át az alapértelmezett beállításokat, ha mást szeretnél: ---

DEFAULT_WINDOWS_VERSION = "win7"    # milyen Windows-verziót szimuláljon a Wine
DEFAULT_RESOLUTION = "1024x768"     # ablakos felbontás (szélesség x magasság)

WINE_PREFIXES_DIR = APP_DATA_DIR / "wineprefixes"


def default_wine_settings() -> dict:
    return {
        "windows_version": DEFAULT_WINDOWS_VERSION,
        "resolution": DEFAULT_RESOLUTION,
    }


def _slugify(name: str) -> str:
    cleaned = "".join(
        char if char.isalnum() else "-"
        for char in str(name).strip().lower()
    ).strip("-")

    return cleaned or "game"


def wine_prefix_path(game: dict) -> Path:
    slug = _slugify(game.get("name", "game"))
    return WINE_PREFIXES_DIR / slug


def wine_env_for_game(game: dict) -> dict:
    env = os.environ.copy()
    env["WINEPREFIX"] = str(wine_prefix_path(game))
    return env


def apply_wine_settings(game: dict) -> None:
    settings = game.get("wine_settings") or default_wine_settings()
    windows_version = settings.get("windows_version", DEFAULT_WINDOWS_VERSION)

    prefix = wine_prefix_path(game)
    prefix.mkdir(parents=True, exist_ok=True)

    env = wine_env_for_game(game)

    try:
        subprocess.run(
            ["wineboot", "--init"],
            env=env,
            check=False,
            capture_output=True,
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        logger.warning("Nem sikerült előkészíteni a Wine-prefixet: %s", error)
        return

    for flag in ("-v", "/v"):
        try:
            result = subprocess.run(
                ["winecfg", flag, windows_version],
                env=env,
                check=False,
                capture_output=True,
                timeout=60,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            logger.warning("Nem sikerült beállítani a Windows-kompatibilitási módot: %s", error)
            return

        if result.returncode == 0:
            return

    logger.warning(
        "A winecfg egyik hívása sem sikerült, a kompatibilitási mód beállítása kimaradt."
    )


def build_wine_command(game: dict, executable_path: str) -> list[str]:
    settings = game.get("wine_settings") or default_wine_settings()
    resolution = settings.get("resolution", DEFAULT_RESOLUTION)

    return [
        "wine",
        "explorer",
        f"/desktop=retro-game-launcher,{resolution}",
        executable_path,
    ]


def build_wine_exec_string(game: dict, executable_path: str, quote) -> str:
    settings = game.get("wine_settings") or default_wine_settings()
    resolution = settings.get("resolution", DEFAULT_RESOLUTION)
    prefix = wine_prefix_path(game)

    command = (
        f"wine explorer /desktop=retro-game-launcher,{resolution} "
        f"{quote(executable_path)}"
    )

    return f'env WINEPREFIX={quote(str(prefix))} {command}'
