# apps/ui/main_window_parts/statusbar.py
# --------------------------------------
# állapotsor frissítése



# Térkép a main_window -hoz:

# apps/
# └── ui/
#    ├── main_window.py              # marad a MainWindow osztály központja
#    └── main_window/
#        ├── __init__.py
#        ├── menus.py                # Fájl / Súgó menük
#        ├── toolbar.py              # eszköztár, Új játék gomb
#    *   ├── statusbar.py            # állapotsor frissítése
#        ├── game_list.py            # lista feltöltése, kijelölés, lista UI
#        └── game_actions.py         # hozzáadás, szerkesztés, törlés, indítás





from PySide6.QtWidgets import QLabel


def setup_status_bar(window):
    """
    Állapotsor létrehozása.
    """

    window.status_games_count_label = QLabel("0 játék")
    window.status_total_size_label = QLabel("Méret összesen: 0 B")
    window.status_selected_size_label = QLabel("Kijelölve: -")

    status_bar = window.statusBar()
    status_bar.addWidget(window.status_games_count_label)
    status_bar.addPermanentWidget(window.status_total_size_label)
    status_bar.addPermanentWidget(window.status_selected_size_label)
