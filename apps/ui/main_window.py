# apps/ui/main_window.py
# ----------------------------


# Térkép a main_window -hoz:

# apps/
# └── ui/
# *  ├── main_window.py                 # marad a MainWindow osztály központja
#    └── main_window_parts/
#           ├── __init__.py
#           ├── menus.py                # Fájl / Súgó menük
#           ├── toolbar.py              # eszköztár, Új játék gomb
#           ├── statusbar.py            # állapotsor frissítése
#           ├── game_list.py            # lista feltöltése, kijelölés, lista UI
#           └── game_actions.py         # hozzáadás, szerkesztés, törlés, indítás



# --- Importok:

from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow

from apps.core.game_store import load_games

# Main_Window_parts:

from apps.ui.main_window_parts.menus import setup_menus
from apps.ui.main_window_parts.statusbar import setup_status_bar
from apps.ui.main_window_parts.central_view import setup_central_view
from apps.ui.main_window_parts.game_list import (
    reload_games,
    setup_game_list_context_menu,

)

from apps.ui.main_window_parts.game_actions import (
    open_add_game_dialog,
    selected_game,
    delete_desktop_file,
    delete_selected_game,
    launch_game_from_row,
    launch_game,
    export_games,
    import_games,
    clear_games,
    properties_selected_game,
)

from apps.ui.main_window_parts.game_helpers import (
    format_size,
    game_size_bytes,
    guess_game_root_path,
    path_size_bytes,
)

from apps.ui.main_window_parts.window_actions import (
    open_settings,
    show_about,
)



from apps.core.logger import get_logger

# --- Importok vége




logger = get_logger(__name__)



class MainWindow(QMainWindow):
    """
    A Retro Game Launcher főablaka.
    """

    def __init__(self):
        super().__init__()

        self._set_window_icon()

        self.setWindowTitle("Retro Game Launcher")
        self.resize(760, 480)

        setup_menus(self)
        setup_status_bar(self)
        setup_central_view(self)

        setup_game_list_context_menu(self)





    def _set_window_icon(self) -> None:
        """
        Alkalmazásikon beállítása a főablakhoz.

        Fejlesztői futtatásnál először a projektben lévő assets/icons mappát
        próbálja használni. Telepített .deb csomagnál a rendszer ikonmappáját.
        Ha egyik sem érhető el, akkor témából próbál általános játék ikont kérni.

        """

        icon_candidates = [
            Path(__file__).resolve().parents[2] / "assets" / "icons" / "game.png",
            Path(__file__).resolve().parents[2] / "packaging" / "icons" / "retro-game-launcher.png",
            Path("/usr/share/icons/hicolor/256x256/apps/retro-game-launcher.png"),
        ]

        for icon_path in icon_candidates:
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
                return

        self.setWindowIcon(QIcon.fromTheme("applications-games"))


    def _update_status_bar(self):
        """
        Frissíti az állapotsor játék- és méretadatait.
        """

        games_count = len(self.games)

        total_size = 0

        for game in self.games:
            game_size = self._game_size_bytes(game)
            total_size += game_size

        logger.debug(
            "Státuszsor frissítve: játékok=%s, összméret=%s",
            games_count,
            self._format_size(total_size),
        )

        self.status_games_count_label.setText(f"{games_count} játék")
        self.status_total_size_label.setText(
            f"Méret összesen: {self._format_size(total_size)}"
        )

        selected_game = self._selected_game()

        if selected_game is None:
            self.status_selected_size_label.setText("Kijelölve: -")
            return

        name = selected_game.get("name", "Névtelen játék")
        selected_size = self._game_size_bytes(selected_game)

        self.status_selected_size_label.setText(
            f"Kijelölve: {name} — {self._format_size(selected_size)}"
        )









    def _open_add_game_dialog(self):
        """
        Megnyitja az új játék hozzáadása ablakot.
        """

        open_add_game_dialog(self)


    def _selected_game(self):
        """
        Visszaadja a táblázatban kijelölt játék adatát.
        """

        return selected_game(self)


    def _delete_desktop_file(self, file_path, error_title):
        """
        Töröl egy .desktop fájlt, ha létezik.
        """

        return delete_desktop_file(self, file_path, error_title)




    def _delete_selected_game(self):
        """
        Eltávolítja a kijelölt játékot a launcher listából,
        és törli a hozzá tartozó .desktop menübejegyzést is.
        """

        delete_selected_game(self)




    def _clear_games(self):
        """
        Teljes játéklista törlése.
        """

        clear_games(self)



    def _properties_selected_game(self):
        properties_selected_game(self)




    def _reload_games(self):
        """
        Újratölti és megjeleníti a felvett játékokat.
        """

        reload_games(self)



    def _launch_game_from_row(self, row):
        """
        Elindítja a táblázat adott sorában lévő játékot.
        """

        launch_game_from_row(self, row)




    def _launch_game(self, game):
        """
        Elindítja a megadott játékot.
        """

        launch_game(self, game)




    def _export_games(self):
        """
        Játéklista mentése külső JSON fájlba.
        """

        export_games(self)


    def _import_games(self):
        """
        Játéklista betöltése külső JSON fájlból.
        """

        import_games(self)







    # --- MainWindow segédfüggvények:

    def _format_size(self, size_bytes):
        """
        Bájt méret olvasható formázása.
        """

        return format_size(size_bytes)

    def _path_size_bytes(self, path: Path) -> int:
        """
        Fájl vagy mappa méretének kiszámítása bájtban.
        """

        return path_size_bytes(path)

    def _game_size_bytes(self, game: dict) -> int:
        """
        Egy játék becsült mérete bájtban.
        """

        return game_size_bytes(game)

    def _guess_game_root_path(self, executable_path: Path) -> Path:
        """
        Megpróbálja megtalálni a játék gyökérmappáját.
        """

        return guess_game_root_path(executable_path)



    # --- MainWindow segédfüggvények vége.





    def _open_settings(self):
        """
        Beállítások ablak megnyitása.
        """

        open_settings(self)




    def _show_about(self):
        """
        Névjegy ablak megjelenítése.
        """

        show_about(self)
