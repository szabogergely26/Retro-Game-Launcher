# apps/ui/main_window_parts/window_actions.py
# ------------------------------------------

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








from PySide6.QtWidgets import QMessageBox
from apps.version_info import ABOUT_DIALOG_VERSION


def open_settings(window):
    """
    Beállítások ablak megnyitása.

    Egyelőre helyőrző, később ide jön majd a valódi SettingsDialog.
    """

    QMessageBox.information(
        window,
        "Beállítások",
        "A beállítások ablak még nincs elkészítve.",
    )


def show_about(window):
    """
    Névjegy ablak megjelenítése.
    """

    about_text = (
        "Retro Game Launcher\n\n"
        f"Verzió: {ABOUT_DIALOG_VERSION}\n\n"
        "Egyszerű indítófelület DOSBox, Wine és natív Linux játékokhoz.\n\n"
        "Fejlesztés kezdete: 2026.05.25\n\n"
    )

    QMessageBox.about(
        window,
        "Névjegy",
        about_text,
    )
