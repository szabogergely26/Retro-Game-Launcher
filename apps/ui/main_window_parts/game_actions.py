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




import json
import subprocess
from pathlib import Path


from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QMessageBox,
    QWizard
)

from apps.core.desktop_writer import (
    create_menu_desktop_launcher,
    create_desktop_icon_launcher,
)

from apps.core.game_store import (
    export_games_to_file,
    import_games_from_file,
    load_games,
    save_games,
)

from apps.ui.add_game_wizard import AddGameWizard
from apps.ui.game_properties_dialog import GamePropertiesDialog

from apps.core.logger import get_logger




logger = get_logger(__name__)

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





def properties_selected_game(window):
    """
    Megnyitja a kijelölt játék Tulajdonságok ablakát.

    Módosítható:
    - név
    - elérési út
    - ikon

    Nem módosítható:
    - indítás típusa

    Opcionálisan létrehozható:
    - asztali parancsikon
    - alkalmazásmenü parancsikon
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
            "Nincs szerkeszthető játék",
            "Ez nem valódi játékbejegyzés.",
        )
        return

    row = window.games_table.currentRow()

    if row < 0 or row >= len(window.games):
        QMessageBox.information(
            window,
            "Nincs kijelölés",
            "Nincs kijelölt játék.",
        )
        return

    dialog = GamePropertiesDialog(game, parent=window)

    if dialog.exec() != QDialog.Accepted:
        return

    updated_game = dialog.data()

    if dialog.should_create_menu_shortcut():
        desktop_path = create_menu_desktop_launcher(
            name=updated_game["name"],
            executable_path=updated_game["executable_path"],
            icon_path=updated_game.get("icon_path", ""),
            launcher_type=updated_game.get("type", "native"),
        )

        updated_game["desktop_path"] = str(desktop_path)
    else:
        menu_shortcut_path = str(game.get("desktop_path", "") or "").strip()

        if menu_shortcut_path:
            try:
                menu_shortcut = Path(menu_shortcut_path).expanduser()

                if menu_shortcut.exists():
                    menu_shortcut.unlink()

                updated_game["desktop_path"] = ""
            except OSError as error:
                QMessageBox.warning(
                    window,
                    "Menü parancsikon törlése sikertelen",
                    f"Nem sikerült törölni az alkalmazásmenü parancsikont:\n\n{error}",
                )
                return




    if dialog.should_create_desktop_shortcut():
        desktop_icon_path = create_desktop_icon_launcher(
            name=updated_game["name"],
            executable_path=updated_game["executable_path"],
            icon_path=updated_game.get("icon_path", ""),
            launcher_type=updated_game.get("type", "native"),
        )

        updated_game["desktop_icon_path"] = str(desktop_icon_path)

    window.games[row] = updated_game
    save_games(window.games)

    subprocess.run(
        ["update-desktop-database", str(Path.home() / ".local/share/applications")],
        check=False,
    )

    window._reload_games()

    window.statusBar().showMessage(
        f"Tulajdonságok mentve: {updated_game.get('name', '')}",
        5000,
    )











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



def clear_games(window):
    """
    Törli a teljes játéklistát.

    A játékfájlokat nem törli, csak a launcher saját listáját üríti.
    """

    if not window.games:
        QMessageBox.information(
            window,
            "Üres játéklista",
            "A játéklista már üres.",
        )
        return

    answer = QMessageBox.question(
        window,
        "Játéklista törlése",
        "Biztosan törlöd a teljes játéklistát?\n\n"
        "Ez csak a launcher listáját üríti ki, a játékfájlokat nem törli.",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No,
    )

    if answer != QMessageBox.Yes:
        return

    save_games([])
    window._reload_games()

    QMessageBox.information(
        window,
        "Játéklista törölve",
        "A játéklista törlése sikerült.",
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

    logger.debug("Játék indítási adatai: %s", game)

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





def export_games(window):
    """
    Játéklista mentése kiválasztott JSON fájlba.
    """

    file_path, _selected_filter = QFileDialog.getSaveFileName(
        window,
        "Játéklista mentése",
        str(Path.home() / "retro-game-launcher-games.json"),
        "JSON fájl (*.json)",
    )

    if not file_path:
        return

    try:
        export_games_to_file(file_path)

    except OSError as error:
        QMessageBox.warning(
            window,
            "Mentési hiba",
            f"A játéklista mentése nem sikerült:\n\n{error}",
        )
        return

    QMessageBox.information(
        window,
        "Játéklista elmentve",
        f"A játéklista mentése sikerült:\n\n{file_path}",
    )


def import_games(window):
    """
    Játéklista betöltése kiválasztott JSON fájlból.
    """

    file_path, _selected_filter = QFileDialog.getOpenFileName(
        window,
        "Játéklista betöltése",
        str(Path.home()),
        "JSON fájl (*.json)",
    )

    if not file_path:
        return

    answer = QMessageBox.question(
        window,
        "Játéklista betöltése",
        "A betöltés felülírja a jelenlegi játéklistát.\n\n"
        "Biztosan folytatod?",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No,
    )

    if answer != QMessageBox.Yes:
        return

    try:
        import_games_from_file(file_path)

    except (OSError, ValueError, json.JSONDecodeError) as error:
        QMessageBox.warning(
            window,
            "Betöltési hiba",
            f"A játéklista betöltése nem sikerült:\n\n{error}",
        )
        return

    window._reload_games()

    QMessageBox.information(
        window,
        "Játéklista betöltve",
        "A játéklista betöltése sikerült.",
    )
