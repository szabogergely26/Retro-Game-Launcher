"""
Retro Game Launcher

Az alkalmazás belépési pontja.
Ez a fájl csak elindítja a PySide6 alkalmazást és megnyitja a főablakot.

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
from apps.core.logger import setup_logging, get_logger

def main():
    """
    QApplication létrehozása és a főablak indítása.
    """

    # Naplózás:
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Retro Game Launcher indítása")


    # Qt alkalmazáspéldány létrehozása.
    app = QApplication(sys.argv)

    # Főablak létrehozása.
    window = MainWindow()

    # Főablak megjelenítése.
    window.show()

    # Qt eseményciklus indítása.
    # Ez addig fut, míg az app be nem záródik.
    exit_code = app.exec()

    logger.info("Retro Game Launcher bezárása")

    return exit_code



if __name__ == "__main__":
    raise SystemExit(main())
