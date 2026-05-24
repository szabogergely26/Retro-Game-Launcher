from PySide6.QtWidgets import QDialog, QVBoxLayout

from apps.ui.launcher_form import LauncherForm


class AddGameDialog(QDialog):
    """
    Új játék hozzáadása ablak.

    Egyelőre a meglévő LauncherForm-ot tartalmazza.
    Később ezt lehet QWizard-ra cserélni.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Új játék hozzáadása")
        self.resize(680, 420)

        layout = QVBoxLayout(self)

        self.launcher_form = LauncherForm()
        layout.addWidget(self.launcher_form)
