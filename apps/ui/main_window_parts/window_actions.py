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

from apps.version_info import CURRENT_STATE
from apps.ui.log_dialog import LogDialog

# Beállítások ablak:
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


# Névjegy ablak:
def show_about(window):
    """
    Névjegy ablak megjelenítése.
    Megjegyzés: új bekezdéshez használj dupla sortörést: \\n\\n
    """

    about_text = (
        "Retro Game Launcher\n\n"
        "Fejlesztői verzió - Rolling\n\n"
        f"Aktuális állapot: {CURRENT_STATE}\n\n"
        "Egyszerű indítófelület DOSBox, Wine és natív Linux játékokhoz.\n\n"
        "Fejlesztés kezdete: 2026.05.25\n\n"
    )

    QMessageBox.about(
        window,
        "Névjegy",
        about_text,
    )


# Napló ablak:
def show_log(window):
    """
    Napló ablak megjelenítése.
    """

    dialog = LogDialog(window)
    dialog.exec()
