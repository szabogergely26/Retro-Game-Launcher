"""
Retro Game Launcher

Az alkalmazás belépési pontja.
Ez a fájl csak elindítja a PySide6 alkalmazást és megnyitja a főablakot.


Aktuális csomagverzió: 0.1.5

Megjegyzés:
A Debian csomag verziója jelenleg még kézzel van kezelve a GitHub Actions
workflow fájlokban.

Frissítéskor ellenőrizendő:
- .github/workflows/build-deb.yml
- .github/workflows/publish-apt-repo.yml
- packaging/debian/control.template, ha később kézzel is módosítjuk

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
