from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QPlainTextEdit,
    QVBoxLayout,
)

from apps.core.logger import LOG_FILE


class LogDialog(QDialog):
    """
    Naplófájl megjelenítése egyszerű olvasható ablakban.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Napló")
        self.resize(900, 600)

        self.log_view = QPlainTextEdit(self)
        self.log_view.setReadOnly(True)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self.log_view)
        layout.addWidget(button_box)

        self._load_log()

    def _load_log(self) -> None:
        log_path = Path(LOG_FILE)

        if not log_path.exists():
            self.log_view.setPlainText(
                f"A naplófájl még nem létezik:\n\n{log_path}"
            )
            return

        try:
            self.log_view.setPlainText(log_path.read_text(encoding="utf-8"))
        except OSError as error:
            self.log_view.setPlainText(
                f"Nem sikerült beolvasni a naplófájlt:\n\n"
                f"{log_path}\n\n"
                f"Hiba: {error}"
            )
