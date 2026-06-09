from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStyle,
    QVBoxLayout,
    QWidget,
)


class IconPreview(QWidget):
    clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(260, 110)

        self._label = QLabel()
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setFixedSize(250, 100)
        self._label.setObjectName("iconPreviewLabel")
        self._label.setStyleSheet(
            """
            QLabel#iconPreviewLabel {
                border: 1px solid #b8b8b8;
                border-radius: 4px;
                background: #f7f7f7;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.set_icon_path(None)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

        super().mousePressEvent(event)

    def set_icon_path(self, icon_path: str | None) -> None:
        if icon_path and Path(icon_path).exists():
            pixmap = QPixmap(icon_path)

            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    64,
                    64,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self._label.setPixmap(scaled)
                return

        empty_file_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        self._label.setPixmap(empty_file_icon.pixmap(64, 64))


class GamePropertiesDialog(QDialog):
    def __init__(self, game: dict, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Tulajdonságok")
        self.setMinimumWidth(680)

        self._original_game = dict(game)
        self._icon_path: str | None = self._get_value(
            game,
            "icon_path",
            "icon",
            "icon_file",
        )

        self.name_edit = QLineEdit()
        self.name_edit.setText(self._get_value(game, "name", "title") or "")

        self.launch_type_edit = QLineEdit()
        self.launch_type_edit.setReadOnly(True)
        self.launch_type_edit.setText(
            self._get_value(
                game,
                "type",
                "launcher_type",
                "launch_type",
            )
            or "native"
        )

        self.executable_edit = QLineEdit()
        self.executable_edit.setText(
            self._get_value(
                game,
                "executable_path",
                "executable",
                "exec_path",
                "path",
            )
            or ""
        )

        self.browse_executable_button = QPushButton("Tallózás...")
        self.browse_executable_button.clicked.connect(self._choose_executable)

        self.icon_preview = IconPreview()
        self.icon_preview.clicked.connect(self._choose_icon)

        self.icon_path_label = QLabel()
        self.icon_path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_path_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.icon_path_label.setWordWrap(True)

        self.browse_icon_button = QPushButton("Ikon módosítása...")
        self.browse_icon_button.clicked.connect(self._choose_icon)

        self.create_desktop_shortcut_checkbox = QCheckBox(
            "Parancsikon létrehozása az asztalra"
        )
        self.create_menu_shortcut_checkbox = QCheckBox(
            "Parancsikon létrehozása az alkalmazásmenübe"
        )

        self._update_icon_preview()
        self._build_ui()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        form_layout.addRow("Név:", self.name_edit)
        form_layout.addRow("Indítás típusa:", self.launch_type_edit)

        executable_layout = QHBoxLayout()
        executable_layout.addWidget(self.executable_edit, stretch=1)
        executable_layout.addWidget(self.browse_executable_button)

        form_layout.addRow("Elérési út:", executable_layout)

        main_layout.addLayout(form_layout)

        main_layout.addSpacing(14)

        main_layout.addWidget(QLabel("Ikon:"))
        main_layout.addWidget(self.icon_preview, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.icon_path_label)
        main_layout.addWidget(
            self.browse_icon_button,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        main_layout.addSpacing(14)

        shortcuts_label = QLabel("Parancsikonok:")
        main_layout.addWidget(shortcuts_label)
        main_layout.addWidget(self.create_desktop_shortcut_checkbox)
        main_layout.addWidget(self.create_menu_shortcut_checkbox)

        main_layout.addStretch(1)

        cancel_button = QPushButton("Mégse")
        cancel_button.clicked.connect(self.reject)

        save_button = QPushButton("Mentés")
        save_button.setDefault(True)
        save_button.clicked.connect(self._accept_if_valid)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)

        main_layout.addLayout(buttons_layout)

    def data(self) -> dict:
        updated_game = dict(self._original_game)

        updated_game["name"] = self.name_edit.text().strip()
        updated_game["executable_path"] = self.executable_edit.text().strip()
        updated_game["icon_path"] = self._icon_path or ""

        # Az indítás típusát szándékosan nem módosítjuk.
        # Csak megjelenítjük readonly mezőben.
        return updated_game

    def should_create_desktop_shortcut(self) -> bool:
        return self.create_desktop_shortcut_checkbox.isChecked()

    def should_create_menu_shortcut(self) -> bool:
        return self.create_menu_shortcut_checkbox.isChecked()

    def _choose_executable(self) -> None:
        current_path = self.executable_edit.text().strip()
        start_dir = str(Path(current_path).parent) if current_path else str(Path.home())

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Elérési út kiválasztása",
            start_dir,
            "Programfájlok (*.exe *.sh *.bat *.com);;Minden fájl (*)",
        )

        if file_path:
            self.executable_edit.setText(file_path)

    def _choose_icon(self) -> None:
        start_dir = (
            str(Path(self._icon_path).parent)
            if self._icon_path
            else str(Path.home())
        )

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Ikon kiválasztása",
            start_dir,
            "Ikonok és képek (*.ico *.png *.jpg *.jpeg *.svg);;Minden fájl (*)",
        )

        if not file_path:
            return

        self._icon_path = file_path
        self._update_icon_preview()

    def _update_icon_preview(self) -> None:
        self.icon_preview.set_icon_path(self._icon_path)

        if self._icon_path:
            self.icon_path_label.setText(self._icon_path)
            self.icon_path_label.show()
        else:
            self.icon_path_label.clear()
            self.icon_path_label.hide()

    def _accept_if_valid(self) -> None:
        name = self.name_edit.text().strip()
        executable_path = self.executable_edit.text().strip()

        if not name:
            QMessageBox.warning(self, "Hiányzó név", "Add meg a játék nevét.")
            return

        if not executable_path:
            QMessageBox.warning(
                self,
                "Hiányzó elérési út",
                "Add meg a játék indítófájlját vagy elérési útját.",
            )
            return

        if not Path(executable_path).exists():
            answer = QMessageBox.question(
                self,
                "Nem létező elérési út",
                "A megadott elérési út nem található.\n\nÍgy is elmented?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if answer != QMessageBox.StandardButton.Yes:
                return

        self.accept()

    @staticmethod
    def _get_value(data: dict, *keys: str) -> str | None:
        for key in keys:
            value = data.get(key)

            if value:
                return str(value)

        return None
