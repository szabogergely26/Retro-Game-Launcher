# Fájl / Súgó menük

# Térkép a main_window -hoz:

# apps/
# └── ui/
#    ├── main_window.py              # marad a MainWindow osztály központja
#    └── main_window/
#        ├── __init__.py
#     *  ├── menus.py                # Fájl / Súgó menük
#        ├── toolbar.py              # eszköztár, Új játék gomb
#        ├── statusbar.py            # állapotsor frissítése
#        ├── game_list.py            # lista feltöltése, kijelölés, lista UI
#        └── game_actions.py         # hozzáadás, szerkesztés, törlés, indítás





from PySide6.QtGui import QAction


def setup_menus(window):
    """A főablak menüsorának felépítése."""

    menubar = window.menuBar()

    file_menu = menubar.addMenu("Fájl")


    save_games_action = file_menu.addAction("Játéklista mentése...")
    save_games_action.triggered.connect(window._export_games)

    load_games_action = file_menu.addAction("Játéklista betöltése...")
    load_games_action.triggered.connect(window._import_games)

    file_menu.addSeparator()

    properties_action = QAction("Tulajdonságok...", window)
    properties_action.triggered.connect(window._properties_selected_game)
    file_menu.addAction(properties_action)

    file_menu.addSeparator()

    clear_games_action = file_menu.addAction("Játéklista törlése...")
    clear_games_action.triggered.connect(window._clear_games)

    file_menu.addSeparator()

    settings_action = QAction("Beállítások...", window)
    settings_action.triggered.connect(window._open_settings)
    file_menu.addAction(settings_action)

    file_menu.addSeparator()

    exit_action = QAction("Kilépés", window)
    exit_action.triggered.connect(window.close)
    file_menu.addAction(exit_action)

    help_menu = menubar.addMenu("Súgó")

    about_action = QAction("Névjegy", window)
    about_action.triggered.connect(window._show_about)
    help_menu.addAction(about_action)
