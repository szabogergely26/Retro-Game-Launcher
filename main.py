"""
Retro Game Launcher

Az alkalmazás belépési pontja.
Ez a fájl csak elindítja a PySide6 alkalmazást és megnyitja a főablakot.
"""

import sys

from PySide6.QtWidgets import QApplication

from apps.ui.main_window import MainWindow


def main():
    """
    QApplication létrehozása és a főablak indítása.
    """

    # Qt alkalmazáspéldány létrehozása.
    app = QApplication(sys.argv)

    # Főablak létrehozása.
    window = MainWindow()

    # Főablak megjelenítése.
    window.show()

    # Qt eseményciklus indítása.
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
