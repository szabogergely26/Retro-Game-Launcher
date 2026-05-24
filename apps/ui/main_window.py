# apps/ui/main_window.py
# ----------------------------

import subprocess
from pathlib import Path

from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
)

from apps.core.game_store import load_games, delete_game_by_desktop_path
from apps.ui.add_game_dialog import AddGameDialog


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
        add_button.setMinimumHeight(38)
        add_button.clicked.connect(self._open_add_game_dialog)

        games_title = QLabel("Felvett játékok")
        games_title.setStyleSheet("font-size: 18px; font-weight: bold;")

        # Itt hozzuk létre a játéklistát.
        # Fontos: ennek meg kell történnie azelőtt,
        # hogy layout.addWidget(self.games_list) lefutna.
        self.games_list = QListWidget()
        self.games_list.setMinimumHeight(220)

        # Dupla kattintásra elindítjuk a kiválasztott játékot.
        self.games_list.itemDoubleClicked.connect(self._launch_selected_game)

        self.delete_button = QPushButton("Kijelölt játék eltávolítása")
        self.delete_button.setMinimumHeight(34)
        self.delete_button.clicked.connect(self._delete_selected_game)

        layout.addWidget(title_label)
        layout.addWidget(self.empty_label)
        layout.addWidget(add_button)
        layout.addWidget(self.games_list)
        layout.addWidget(self.delete_button)
        layout.addStretch()


        self.setCentralWidget(central_widget)

        # Miután a lista widget már létezik, betöltjük a játékokat.
        self._reload_games()

    def _open_add_game_dialog(self):
        """
        Megnyitja az új játék hozzáadása ablakot.
        """

        dialog = AddGameDialog(self)
        dialog.exec()

         # A dialógus bezárása után újratöltjük a játéklistát.
        self._reload_games()




    def _delete_selected_game(self):
        """
        Eltávolítja a kijelölt játékot a launcher listából,
        és törli a hozzá tartozó .desktop menübejegyzést is.
        """

        item = self.games_list.currentItem()

        if item is None:
            QMessageBox.information(
                self,
                "Nincs kijelölés",
                "Nincs kijelölt játék."
            )
            return

        game = item.data(1000)

        if not game:
            QMessageBox.information(
                self,
                "Nincs törölhető játék",
                "Ez nem valódi játékbejegyzés."
            )
            return

        name = game.get("name", "Névtelen játék")
        desktop_path = game.get("desktop_path", "")

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

        # A játék törlése a games.json-ból.
        delete_game_by_desktop_path(desktop_path)

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



    def _reload_games(self):
        """
        Újratölti és megjeleníti a felvett játékokat.
        """

        self.games_list.clear()

        games = load_games()

        self.empty_label.setVisible(not games)

        if not games:
            return

        for game in games:
            name = game.get("name", "Névtelen játék")
            launcher_type = game.get("launcher_type", "Ismeretlen típus")
            executable_path = game.get("executable_path", "")

            item_text = f"{name}    |    {launcher_type}"

            if executable_path:
                item_text += f"\n{executable_path}"

            item = QListWidgetItem(item_text)

            # Az adott listaelemhez eltároljuk a teljes játék-adatot.
            # Így dupla kattintáskor vissza tudjuk olvasni.
            item.setData(1000, game)

            self.games_list.addItem(item)




    def _launch_selected_game(self, item):
        """
        Elindítja a kiválasztott játékot.

        Első körben ellenőrizzük, hogy nem DOS-os fájlt próbálunk-e
        natív Linux programként indítani.

        Ezután a .desktop fájlt próbáljuk indítani.
        Ha az nincs, akkor az executable_path alapján próbálkozunk.
        """

        game = item.data(1000)

        if not game:
            return

        desktop_path = game.get("desktop_path", "")
        executable_path = game.get("executable_path", "")

        # A játék típusa: például "native" vagy "dosbox".
        game_type = game.get("type", "native")

        # DOS-os fájlkiterjesztések, amelyeket nem akarunk natív Linux programként futtatni.
        dos_extensions = (".exe", ".bat", ".com")

        # Ha DOS-os fájlt próbálnánk natívként indítani, megállunk és szólunk.
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

        # Ha van .desktop fájl, azt indítjuk.
        if desktop_path and Path(desktop_path).exists():
            subprocess.Popen(["gtk-launch", Path(desktop_path).stem])
            return

        # Ha nincs .desktop fájl, de van indítófájl, azt próbáljuk futtatni.
        if executable_path and Path(executable_path).exists():
            subprocess.Popen([executable_path])
            return

        QMessageBox.warning(
            self,
            "Nem található indítható fájl",
            "Nem található .desktop fájl vagy érvényes indítófájl ehhez a játékhoz."
        )
