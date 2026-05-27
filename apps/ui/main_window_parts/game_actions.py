# apps/ui/main_window_parts/game_actions.py
# -------------------------------------------


# hozzáadás, szerkesztés, törlés, indítás

# Térkép a main_window -hoz:

# apps/
# └── ui/
#    ├── main_window.py              # marad a MainWindow osztály központja
#    └── main_window/
#        ├── __init__.py
#        ├── menus.py                # Fájl / Súgó menük
#        ├── toolbar.py              # eszköztár, Új játék gomb
#        ├── statusbar.py            # állapotsor frissítése
#        ├── game_list.py            # lista feltöltése, kijelölés, lista UI
#     *  └── game_actions.py         # hozzáadás, szerkesztés, törlés, indítás





import subprocess
from pathlib import Path

from PySide6.QtWidgets import QMessageBox, QWizard

from apps.core.desktop_writer import (
    create_menu_desktop_launcher,
    create_desktop_icon_launcher,
)

from apps.core.game_store import load_games, save_games

from apps.ui.add_game_wizard import AddGameWizard






def open_add_game_dialog(window):
    """
    Megnyitja az új játék hozzáadása ablakot.
    """

    wizard = AddGameWizard(window)

    if wizard.exec() != QWizard.Accepted:
        return

    game_data = wizard.get_game_data()

    games = load_games()

    new_name = str(game_data.get("name", "")).strip().casefold()
    new_path = str(game_data.get("executable_path", "")).strip()

    for existing_game in games:
        existing_name = str(existing_game.get("name", "")).strip().casefold()
        existing_path = str(existing_game.get("executable_path", "")).strip()

        if new_path and existing_path and new_path == existing_path:
            QMessageBox.warning(
                window,
                "Duplikált játék",
                "Ez az indítófájl már szerepel a launcherben.\n\n"
                f"{game_data.get('executable_path', '')}",
            )
            return

        if new_name and existing_name and new_name == existing_name:
            QMessageBox.warning(
                window,
                "Duplikált játék",
                "Ilyen nevű játék már szerepel a launcherben.\n\n"
                f"{game_data.get('name', '')}",
            )
            return

    if wizard.should_create_menu_icon():
        desktop_path = create_menu_desktop_launcher(
            name=game_data["name"],
            executable_path=game_data["executable_path"],
            icon_path=game_data["icon_path"],
            launcher_type=game_data["type"],
        )

        game_data["desktop_path"] = str(desktop_path)

    if wizard.should_create_desktop_icon():
        desktop_icon_path = create_desktop_icon_launcher(
            name=game_data["name"],
            executable_path=game_data["executable_path"],
            icon_path=game_data["icon_path"],
            launcher_type=game_data["type"],
        )

        game_data["desktop_icon_path"] = str(desktop_icon_path)

    games.append(game_data)
    save_games(games)

    window._reload_games()


def selected_game(window):
    """
    Visszaadja a táblázatban kijelölt játék adatát.
    """

    row = window.games_table.currentRow()

    if row < 0:
        return None

    if row >= len(window.games):
        return None

    return window.games[row]


def delete_desktop_file(window, file_path, error_title):
    """
    Töröl egy .desktop fájlt, ha létezik.
    """

    if not file_path:
        return True

    desktop_file = Path(file_path)

    if not desktop_file.exists():
        return True

    try:
        desktop_file.unlink()
        return True

    except OSError as error:
        QMessageBox.warning(
            window,
            error_title,
            f"A .desktop fájlt nem sikerült törölni:\n\n{error}",
        )

    return False


def delete_selected_game(window):
    """
    Eltávolítja a kijelölt játékot a launcher listából,
    és törli a hozzá tartozó .desktop fájlokat is.
    """

    game = window._selected_game()

    if game is None:
        QMessageBox.information(
            window,
            "Nincs kijelölés",
            "Nincs kijelölt játék.",
        )
        return

    if not game:
        QMessageBox.information(
            window,
            "Nincs törölhető játék",
            "Ez nem valódi játékbejegyzés.",
        )
        return

    name = game.get("name", "Névtelen játék")
    desktop_path = game.get("desktop_path", "")
    desktop_icon_path = game.get("desktop_icon_path", "")

    answer = QMessageBox.question(
        window,
        "Játék eltávolítása",
        f"Biztosan eltávolítod ezt a játékot?\n\n{name}\n\n"
        "A launcher listából és a menübejegyzések közül is törlődni fog.",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No,
    )

    if answer != QMessageBox.Yes:
        return

    row = window.games_table.currentRow()

    if row < 0 or row >= len(window.games):
        QMessageBox.information(
            window,
            "Nincs kijelölés",
            "Nincs kijelölt játék.",
        )
        return

    if not window._delete_desktop_file(
        desktop_path,
        "Menübejegyzés törlési hiba",
    ):
        return

    if not window._delete_desktop_file(
        desktop_icon_path,
        "Asztali ikon törlési hiba",
    ):
        return

    window.games.pop(row)
    save_games(window.games)

    subprocess.run(
        ["update-desktop-database", str(Path.home() / ".local/share/applications")],
        check=False,
    )

    window._reload_games()

    QMessageBox.information(
        window,
        "Játék eltávolítva",
        f"A játék eltávolítva:\n\n{name}",
    )


def launch_game_from_row(window, row):
    """
    Elindítja a táblázat adott sorában lévő játékot.
    """

    if row < 0 or row >= len(window.games):
        return

    window._launch_game(window.games[row])


def launch_game(window, game):
    """
    Elindítja a megadott játékot.
    """

    print("DEBUG GAME:", game)

    if not game:
        return

    desktop_path = game.get("desktop_path", "")
    executable_path = game.get("executable_path", "")

    game_type = str(game.get("type", "native")).lower()

    dos_extensions = (".exe", ".bat", ".com")

    if (
        game_type == "native"
        and executable_path
        and executable_path.lower().endswith(dos_extensions)
    ):
        QMessageBox.warning(
            window,
            "Nem megfelelő indítási típus",
            "Ez DOS-os indítófájlnak tűnik, de a játék típusa natívra van állítva.\n\n"
            "Állítsd át a játék típusát DOSBox-ra, majd próbáld újra.",
        )
        return

    if desktop_path and Path(desktop_path).exists():
        subprocess.Popen(["gtk-launch", Path(desktop_path).stem])
        return

    if executable_path and Path(executable_path).exists():
        if game_type == "dosbox":
            subprocess.Popen(["dosbox", executable_path])
            return

        if game_type == "wine":
            subprocess.Popen(["wine", executable_path])
            return

        if game_type == "native":
            subprocess.Popen([executable_path])
            return

    QMessageBox.warning(
        window,
        "Ismeretlen indítási típus",
        f"Nem támogatott vagy nem indítható játék:\n\n{game_type}",
    )


