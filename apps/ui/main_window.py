# apps/ui/main_window.py
# ----------------------------


# Térkép a main_window -hoz:

# apps/
# └── ui/
# *  ├── main_window.py              # marad a MainWindow osztály központja
#    └── main_window/
#        ├── __init__.py
#        ├── menus.py                # Fájl / Súgó menük
#        ├── toolbar.py              # eszköztár, Új játék gomb
#        ├── statusbar.py            # állapotsor frissítése
#        ├── game_list.py            # lista feltöltése, kijelölés, lista UI
#        └── game_actions.py         # hozzáadás, szerkesztés, törlés, indítás



# --- Importok:
import subprocess
from pathlib import Path

from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QMessageBox,
    QWizard,
    QDialog,
)

from apps.core.desktop_writer import (
    create_menu_desktop_launcher,
    create_desktop_icon_launcher,

)

from apps.core.game_store import (
    load_games,
    save_games
)

from apps.ui.add_game_wizard import AddGameWizard
from apps.ui.edit_game_dialog import EditGameDialog


from apps.ui.main_window_parts.menus import setup_menus


# --- Importok vége


GAME_TYPE_LABELS = {
    "dosbox": "DOSBox",
    "wine": "Wine",
    "native": "Natív Linux",
    "linux": "Natív Linux",
}


# --- Segédfüggvény:

def game_type_label(game_type: str) -> str:
    return GAME_TYPE_LABELS.get(str(game_type).lower(), "Ismeretlen típus")



class MainWindow(QMainWindow):
    """
    A Retro Game Launcher főablaka.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Retro Game Launcher")
        self.resize(760, 480)

        setup_menus(self)
        self._build_status_bar()
        self._build_central_view()



    def _build_central_view(self):
        """
        A fő launcher nézet létrehozása.
        """

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title_label = QLabel("Retro Game Launcher")
        title_label.setStyleSheet("font-size: 26px; font-weight: bold;")

        self.empty_label = QLabel("Még nincs felvett játék.")
        self.empty_label.setStyleSheet("font-size: 15px;")


        add_button = QPushButton("Új játék hozzáadása")
        add_button.setMinimumHeight(20)
        add_button.setFixedWidth(150)
        add_button.clicked.connect(self._open_add_game_dialog)

        games_title = QLabel("Felvett játékok")
        games_title.setStyleSheet("font-size: 18px; font-weight: bold;")

        fullscreen_hint = QLabel("Teljes képernyő: ALT+Enter")
        fullscreen_hint.setStyleSheet("font-size: 12px;")

        exit_hint = QLabel("Kilépéshez írd be: exit")
        exit_hint.setStyleSheet("font-size: 12px;")

        self.games_table = QTableWidget()
        self.games_table.setColumnCount(3)
        self.games_table.setHorizontalHeaderLabels(["Név", "Típus", "Művelet"])
        self.games_table.setMinimumHeight(220)

        self.games_table.verticalHeader().setVisible(False)
        self.games_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.games_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.games_table.setSelectionMode(QAbstractItemView.SingleSelection)

        header = self.games_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)


        # Dupla kattintás:
        self.games_table.cellDoubleClicked.connect(
            lambda row, _column: self._launch_game_from_row(row)
        )

        # kattintásra megjelenik az aktuális infó:
        self.games_table.itemSelectionChanged.connect(self._update_status_bar)

        self.delete_button = QPushButton("Eltávolítás")
        self.delete_button.setMinimumHeight(20)
        self.delete_button.setFixedWidth(180)
        self.delete_button.clicked.connect(self._delete_selected_game)

        layout.addWidget(title_label)
        layout.addWidget(self.empty_label)


        hint_layout = QVBoxLayout()
        # hint_layout.setContentsMargins(0, 0, 0, 0) bal, felül, jobb, alul
        hint_layout.setContentsMargins(80, 0, 0, 0)
        hint_layout.setSpacing(1)
        hint_layout.addWidget(fullscreen_hint)
        hint_layout.addWidget(exit_hint)

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(12)
        top_layout.addWidget(add_button)
        top_layout.addLayout(hint_layout)
        top_layout.addStretch()


        layout.addLayout(top_layout)

        layout.addWidget(games_title)
        layout.addWidget(self.games_table)
        layout.addWidget(self.delete_button)
        layout.addStretch()


        self.setCentralWidget(central_widget)

        # Miután a lista widget már létezik, betöltjük a játékokat.
        self._reload_games()




    def _build_status_bar(self):
        """
        Állapotsor létrehozása.
        """

        self.status_games_count_label = QLabel("0 játék")
        self.status_total_size_label = QLabel("Méret összesen: 0 B")
        self.status_selected_size_label = QLabel("Kijelölve: -")

        status_bar = self.statusBar()
        status_bar.addWidget(self.status_games_count_label)
        status_bar.addPermanentWidget(self.status_total_size_label)
        status_bar.addPermanentWidget(self.status_selected_size_label)





    def _update_status_bar(self):
        """
        Frissíti az állapotsor játék- és méretadatait.
        """

        games_count = len(self.games)

        total_size = 0

        for game in self.games:
            game_size = self._game_size_bytes(game)
            total_size += game_size

            print(
                "DEBUG SIZE:",
                game.get("name", "Névtelen játék"),
                self._format_size(game_size),
                game.get("executable_path", ""),
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
        wizard = AddGameWizard(self)

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
                self,
                "Duplikált játék",
                "Ez az indítófájl már szerepel a launcherben.\n\n"
                f"{game_data.get('executable_path', '')}",
            )
            return

        if new_name and existing_name and new_name == existing_name:
            QMessageBox.warning(
                self,
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

        self._reload_games()



    def _selected_game(self):
        """
        Visszaadja a táblázatban kijelölt játék adatát.
        """

        row = self.games_table.currentRow()

        if row < 0:
            return None

        if row >= len(self.games):
            return None

        return self.games[row]


    def _delete_desktop_file(self, file_path, error_title):
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
                self,
                error_title,
                f"A .desktop fájlt nem sikerült törölni:\n\n{error}"
            )
        return False




    def _delete_selected_game(self):
        """
        Eltávolítja a kijelölt játékot a launcher listából,
        és törli a hozzá tartozó .desktop menübejegyzést is.
        """

        game = self._selected_game()

        if game is None:
            QMessageBox.information(
                self,
                "Nincs kijelölés",
                "Nincs kijelölt játék."
            )
            return

        if not game:
            QMessageBox.information(
                self,
                "Nincs törölhető játék",
                "Ez nem valódi játékbejegyzés."
            )
            return

        name = game.get("name", "Névtelen játék")
        desktop_path = game.get("desktop_path", "")
        desktop_icon_path = game.get("desktop_icon_path", "")

        answer = QMessageBox.question(
            self,
            "Játék eltávolítása",
            f"Biztosan eltávolítod ezt a játékot?\n\n{name}\n\n"
            "A launcher listából és a menübejegyzések közül is törlődni fog.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if answer != QMessageBox.Yes:
            return

        # Ha van hozzá .desktop fájl, töröljük a menüből.
        if desktop_path:
            desktop_file = Path(desktop_path)

            if desktop_file.exists():
                try:
                    desktop_file.unlink()

                except OSError as error:
                    QMessageBox.warning(
                        self,
                        "Menübejegyzés törlési hiba",
                        f"A .desktop fájlt nem sikerült törölni:\n\n{error}"
                    )
                    return

        row = self.games_table.currentRow()

        if row < 0 or row >= len(self.games):
            QMessageBox.information(
                self,
                "Nincs kijelölés",
                "Nincs kijelölt játék."
            )
            return

        # Menübejegyzés törlése, ha készült.
        if not self._delete_desktop_file(
            desktop_path,
            "Menübejegyzés törlési hiba",
        ):
            return

        # Asztali ikon törlése, ha készült.
        if not self._delete_desktop_file(
            desktop_icon_path,
            "Asztali ikon törlési hiba",
        ):
            return

        # A játék törlése a launcher saját listájából.
        self.games.pop(row)
        save_games(self.games)

        # Menük frissítése Linux alatt.
        subprocess.run(
            ["update-desktop-database", str(Path.home() / ".local/share/applications")],
            check=False,
        )

        # Lista újratöltése.
        self._reload_games()

        QMessageBox.information(
            self,
            "Játék eltávolítva",
            f"A játék eltávolítva:\n\n{name}"
        )



        self._reload_games()


    def _reload_games(self):
        """
        Újratölti és megjeleníti a felvett játékokat.
        """

        self.games = sorted(
            load_games(),
            key=lambda game: str(game.get("name", "")).casefold(),
        )

        self.games_table.setRowCount(0)

        self.empty_label.setVisible(len(self.games) == 0)
        self.games_table.setVisible(len(self.games) > 0)
        self.delete_button.setEnabled(len(self.games) > 0)

        for game in self.games:
            row = self.games_table.rowCount()
            self.games_table.insertRow(row)

            name = game.get("name", "Névtelen játék")
            game_type = game.get("type", "")

            name_item = QTableWidgetItem(name)
            type_item = QTableWidgetItem(game_type_label(game_type))

            launch_button = QPushButton("Indítás")
            launch_button.setFixedWidth(80)
            launch_button.clicked.connect(
                lambda checked=False, selected_game=game: self._launch_game(selected_game)
            )

            self.games_table.setItem(row, 0, name_item)
            self.games_table.setItem(row, 1, type_item)
            self.games_table.setCellWidget(row, 2, launch_button)


        self._update_status_bar()



    def _launch_game_from_row(self, row):
        """
        Elindítja a táblázat adott sorában lévő játékot.
        """

        if row < 0 or row >= len(self.games):
            return

        self._launch_game(self.games[row])


    def _launch_game(self, game):
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
                self,
                "Nem megfelelő indítási típus",
                "Ez DOS-os indítófájlnak tűnik, de a játék típusa natívra van állítva.\n\n"
                "Állítsd át a játék típusát DOSBox-ra, majd próbáld újra."
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
            self,
            "Ismeretlen indítási típus",
            f"Nem támogatott vagy nem indítható játék:\n\n{game_type}"
        )





    def _edit_selected_game(self) -> None:
        game = self._selected_game()

        if game is None:
            QMessageBox.information(
                self,
                "Nincs kijelölt játék",
                "Előbb jelölj ki egy játékot a szerkesztéshez.",
            )
            return

        dialog = EditGameDialog(game, self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        updated_game = dialog.data()

        if dialog.should_create_desktop_icon():
            desktop_icon_path = create_desktop_icon_launcher(
                name=updated_game["name"],
                executable_path=updated_game["executable_path"],
                icon_path=updated_game.get("icon_path", ""),
                launcher_type=updated_game.get("type", "native"),
            )

            updated_game["desktop_icon_path"] = str(desktop_icon_path)

            QMessageBox.information(
                self,
                "Asztali ikon létrehozva",
                f"Az asztali ikon elkészült:\n\n{desktop_icon_path}",
            )




        self._update_game(game, updated_game)

        self._reload_games()




    # Mentés:
    def _update_game(self, old_game: dict, updated_game: dict) -> None:
        old_game.clear()
        old_game.update(updated_game)
        save_games(self.games)








    # --- MainWindow segédfüggvények:

    # Méretformázó helper:
    def _format_size(self, size_bytes):
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


    # Könyvtár-méret számoló:
    def _path_size_bytes(self, path: Path) -> int:
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



    def _game_size_bytes(self, game: dict) -> int:
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
            return self._path_size_bytes(path)

        if game_type == "dosbox":
            game_root = self._guess_game_root_path(path)
            return self._path_size_bytes(game_root)

        if game_type == "wine":
            return self._path_size_bytes(path.parent)

        return self._path_size_bytes(path)



    def _guess_game_root_path(self, executable_path: Path) -> Path:
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


    # MainWindow segédfüggvények vége.


    def _open_settings(self):
        """
        Beállítások ablak megnyitása.

        Egyelőre helyőrző, később ide jön majd a valódi SettingsDialog.
        """

        QMessageBox.information(
            self,
            "Beállítások",
            "A beállítások ablak még nincs elkészítve.",
        )


    def _show_about(self):
        """
        Névjegy ablak megjelenítése.
        """

        about_text = (
            "Retro Game Launcher\n\n"
            "Egyszerű indítófelület DOSBox, Wine és natív Linux játékokhoz.\n\n"
            "Fejlesztés kezdete: 2026.05.25"
        )

        QMessageBox.about(
            self,
            "Névjegy",
            about_text,
        )
