"""
Retro Game Launcher - főablak

Ebben a fájlban van az alkalmazás főablaka.
A tényleges indító-készítő űrlap külön fájlban van: launcher_form.py
"""

from PySide6.QtWidgets import QMainWindow

from apps.ui.launcher_form import LauncherForm


class MainWindow(QMainWindow):
    """
    A Retro Game Launcher főablaka.
    """

    def __init__(self):
        super().__init__()

        # Ablak alapbeállításai.
        self.setWindowTitle("Retro Game Launcher")
        self.resize(760, 480)

        # A főablak központi tartalma az indító-készítő űrlap.
        self.launcher_form = LauncherForm()
        self.setCentralWidget(self.launcher_form)
