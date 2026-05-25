# apps/ui/main_window.py
# ----------------------------

# --- Importok:
import subprocess
from pathlib import Path

from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QPushButton,
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

        self._build_menu()
        self._build_central_view()

    def _build_menu(self):
        """
        Főmenü létrehozása.
        """

        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("Fájl")

        new_game_action = file_menu.addAction("Új játék hozzáadása")
        new_game_action.triggered.connect(self._open_add_game_dialog)

        file_menu.addSeparator()

        edit_game_action = file_menu.addAction("Szerkesztés")
        edit_game_action.triggered.connect(self._edit_selected_game)

        exit_action = file_menu.addAction("Kilépés")
        exit_action.triggered.connect(self.close)

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
        games_title = QLabel("Teljes képernyő: ALT+Enter")
        games_title.setStyleSheet("font-size: 18px;")

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

        self.games_table.cellDoubleClicked.connect(
            lambda row, _column: self._launch_game_from_row(row)
        )

        self.delete_button = QPushButton("Eltávolítás")
        self.delete_button.setMinimumHeight(20)
        self.delete_button.setFixedWidth(180)
        self.delete_button.clicked.connect(self._delete_selected_game)

        layout.addWidget(title_label)
        layout.addWidget(self.empty_label)
        layout.addWidget(add_button)
        layout.addWidget(games_title)
        layout.addWidget(self.games_table)
        layout.addWidget(self.delete_button)
        layout.addStretch()


        self.setCentralWidget(central_widget)

        # Miután a lista widget már létezik, betöltjük a játékokat.
        self._reload_games()

    def _open_add_game_dialog(self):
        """
        Megnyitja az új játék hozzáadása ablakot.
        """
        wizard = AddGameWizard(self)

        if wizard.exec() != QWizard.Accepted:
            return

        game_data = wizard.get_game_data()

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

        games = load_games()
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

        self.games = load_games()

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

        game_type = game.get("type", "native")

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
