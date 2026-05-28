# apps/ui/main_window_parts/game_helpers.py
# ----------------------------------------


# Térkép a main_window -hoz:
#
# apps/
# └── ui/
#    ├── main_window.py                 # marad a MainWindow osztály központja
#    └── main_window_parts/
#           ├── __init__.py
#           ├── menus.py                # Fájl / Súgó menük
#           ├── toolbar.py              # eszköztár, Új játék gomb
#           ├── statusbar.py            # állapotsor létrehozása
#           ├── central_view.py         # fő launcher nézet felépítése
# *         ├── game_helpers.py         # játékadatokhoz tartozó segédfüggvények
#           ├── game_list.py            # lista feltöltése, kijelölés, lista UI
#           └── game_actions.py         # hozzáadás, szerkesztés, törlés, indítás


from pathlib import Path



GAME_TYPE_LABELS = {
    "dosbox": "DOSBox",
    "wine": "Wine",
    "native": "Natív Linux",
    "linux": "Natív Linux",
}


def game_type_label(game_type: str) -> str:
    """
    Játéktípus belső azonosítójának emberi olvasható felirattá alakítása.
    """

    return GAME_TYPE_LABELS.get(str(game_type).lower(), "Ismeretlen típus")









def format_size(size_bytes):
    """
    Bájt méret olvasható formázása.
    """

    if not size_bytes:
        return "0 B"

    size = float(size_bytes)
    units = ["B", "KB", "MB", "GB", "TB"]

    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"

            return f"{size:.1f} {unit}".replace(".", ",")

        size /= 1024

    return "0 B"


def path_size_bytes(path: Path) -> int:
    """
    Fájl vagy mappa méretének kiszámítása bájtban.
    """

    if not path.exists():
        return 0

    if path.is_file():
        return path.stat().st_size

    total_size = 0

    for item in path.rglob("*"):
        if item.is_file():
            try:
                total_size += item.stat().st_size
            except OSError:
                pass

    return total_size


def game_size_bytes(game: dict) -> int:
    """
    Egy játék becsült mérete bájtban.

    DOSBox játékoknál a DOS gyűjtőmappa alatti játékgyökeret méri.
    Wine játékoknál az indítófájl mappáját.
    Natív Linux programnál magát az indítófájlt.
    """

    executable_path = game.get("executable_path", "")

    if not executable_path:
        return 0

    path = Path(executable_path)

    if not path.exists():
        return 0

    game_type = str(game.get("type", "native")).lower()

    if path.is_dir():
        return path_size_bytes(path)

    if game_type == "dosbox":
        game_root = guess_game_root_path(path)
        return path_size_bytes(game_root)

    if game_type == "wine":
        return path_size_bytes(path.parent)

    return path_size_bytes(path)


def guess_game_root_path(executable_path: Path) -> Path:
    """
    Megpróbálja megtalálni a játék gyökérmappáját.

    Példa:
    /home/szaboger/Retro-jatekok/DOS/F22/F22/F22.EXE
    -> /home/szaboger/Retro-jatekok/DOS/F22
    """

    parts = executable_path.parts

    if "DOS" in parts:
        dos_index = parts.index("DOS")

        if len(parts) > dos_index + 1:
            return Path(*parts[:dos_index + 2])

    return executable_path.parent
