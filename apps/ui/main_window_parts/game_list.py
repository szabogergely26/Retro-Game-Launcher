# apps/ui/main_window_parts/game_list.py
# -------------------------------------

# lista feltöltése, kijelölés, lista UI

# Térkép a main_window -hoz:

# apps/
# └── ui/
#    ├── main_window.py              # marad a MainWindow osztály központja
#    └── main_window/
#        ├── __init__.py
#        ├── menus.py                # Fájl / Súgó menük
#        ├── toolbar.py              # eszköztár, Új játék gomb
#        ├── statusbar.py            # állapotsor frissítése
#   *    ├── game_list.py            # Játéklista betöltése és táblázat frissítése
#        └── game_actions.py         # hozzáadás, szerkesztés, törlés, indítás



from PySide6.QtWidgets import QPushButton, QTableWidgetItem

from apps.core.game_store import load_games
from apps.ui.main_window_parts.game_helpers import game_type_label


def reload_games(window):
    """
    Újratölti és megjeleníti a felvett játékokat.
    """

    window.games = sorted(
        load_games(),
        key=lambda game: str(game.get("name", "")).casefold(),
    )

    window.games_table.setRowCount(0)

    window.empty_label.setVisible(len(window.games) == 0)
    window.games_table.setVisible(len(window.games) > 0)
    window.delete_button.setEnabled(len(window.games) > 0)

    for game in window.games:
        row = window.games_table.rowCount()
        window.games_table.insertRow(row)

        name = game.get("name", "Névtelen játék")
        game_type = game.get("type", "")

        name_item = QTableWidgetItem(name)
        type_item = QTableWidgetItem(game_type_label(game_type))

        launch_button = QPushButton("Indítás")
        launch_button.setFixedWidth(80)
        launch_button.clicked.connect(
            lambda checked=False, selected_game=game: window._launch_game(selected_game)
        )

        window.games_table.setItem(row, 0, name_item)
        window.games_table.setItem(row, 1, type_item)
        window.games_table.setCellWidget(row, 2, launch_button)

    window._update_status_bar()
