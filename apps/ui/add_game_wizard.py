from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWizard,
    QWizardPage,
    QWidget,
    QComboBox,
)


class IntroPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Új játék hozzáadása")
        self.setSubTitle("Ez a varázsló segít új játékot felvenni a launcher listájába.")

        label = QLabel(
            "A játék a launcher saját listájába kerül.\n\n"
            "A befejezésnél külön eldöntheted, hogy szeretnél-e "
            "Linux alkalmazásmenübe kerülő indítóikont is létrehozni."
        )
        label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)


class GameDataPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Játék adatai")
        self.setSubTitle("Add meg a játék nevét, indítófájlját, ikonját és indítási típusát.")

        self.name_edit = QLineEdit()
        self.executable_edit = QLineEdit()
        self.icon_edit = QLineEdit()

        self.runner_combo = QComboBox()
        self.runner_combo.addItem("Natív / közvetlen indítás", "native")
        self.runner_combo.addItem("DOSBox", "dosbox")
        self.runner_combo.addItem("Wine", "wine")
        self.runner_combo.addItem("Egyedi parancs", "custom")

        executable_button = QPushButton("Tallózás…")
        executable_button.clicked.connect(self._browse_executable)

        icon_button = QPushButton("Tallózás…")
        icon_button.clicked.connect(self._browse_icon)

        executable_row = QWidget()
        executable_layout = QVBoxLayout()
        executable_layout.setContentsMargins(0, 0, 0, 0)
        executable_layout.addWidget(self.executable_edit)
        executable_layout.addWidget(executable_button)
        executable_row.setLayout(executable_layout)

        icon_row = QWidget()
        icon_layout = QVBoxLayout()
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.addWidget(self.icon_edit)
        icon_layout.addWidget(icon_button)
        icon_row.setLayout(icon_layout)

        layout = QFormLayout()
        layout.addRow("Játék neve:", self.name_edit)
        layout.addRow("Indítófájl:", executable_row)
        layout.addRow("Ikonfájl:", icon_row)
        layout.addRow("Indítási típus:", self.runner_combo)

        self.setLayout(layout)

    def _browse_executable(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Indítófájl kiválasztása",
            str(Path.home()),
        )

        if file_path:
            self.executable_edit.setText(file_path)

    def _browse_icon(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Ikonfájl kiválasztása",
            str(Path.home()),
            "Képfájlok (*.png *.jpg *.jpeg *.svg *.ico);;Minden fájl (*)",
        )

        if file_path:
            self.icon_edit.setText(file_path)

    def validatePage(self):
        name = self.name_edit.text().strip()
        executable_path = self.executable_edit.text().strip()
        runner = self.runner_combo.currentData()

        if not name:
            QMessageBox.warning(
                self,
                "Hiányzó név",
                "Add meg a játék nevét."
            )
            return False

        if not executable_path:
            QMessageBox.warning(
                self,
                "Hiányzó indítófájl",
                "Válassz indítófájlt a játékhoz."
            )
            return False

        if not Path(executable_path).exists():
            QMessageBox.warning(
                self,
                "Nem található indítófájl",
                "A megadott indítófájl nem található."
            )
            return False

        if runner == "native" and executable_path.lower().endswith((".exe", ".bat", ".com")):
            QMessageBox.warning(
                self,
                "Gyanús indítási típus",
                "DOS-os vagy Windows-os indítófájlt választottál, "
                "de az indítási típus natívra van állítva.\n\n"
                "DOS-os játékhoz válaszd a DOSBox típust."
            )
            return False

        return True


class FinishPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Befejezés")
        self.setSubTitle("A játék felvételre kész.")

        label = QLabel(
            "A Befejezés gombra kattintva a játék bekerül a launcher saját listájába.\n\n"
            "Ha szeretnéd, külön indítóikon is létrehozható hozzá az alkalmazásmenübe."
        )
        label.setWordWrap(True)

        self.create_menu_icon_checkbox = QCheckBox(
            "Indítóikon létrehozása az alkalmazásmenübe"
        )
        self.create_menu_icon_checkbox.setChecked(False)



        self.create_desktop_icon_checkbox = QCheckBox(
            "Asztali ikon létrehozása"
        )
        self.create_desktop_icon_checkbox.setChecked(False)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.create_menu_icon_checkbox)
        self.setLayout(layout)
        layout.addWidget(self.create_desktop_icon_checkbox)


class AddGameWizard(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Új játék hozzáadása")

        self.intro_page = IntroPage()
        self.game_data_page = GameDataPage()
        self.finish_page = FinishPage()

        self.addPage(self.intro_page)
        self.addPage(self.game_data_page)
        self.addPage(self.finish_page)

        self.setOption(QWizard.NoBackButtonOnStartPage, True)

    def get_game_data(self):
        return {
            "name": self.game_data_page.name_edit.text().strip(),
            "executable_path": self.game_data_page.executable_edit.text().strip(),
            "icon_path": self.game_data_page.icon_edit.text().strip(),
            "type": self.game_data_page.runner_combo.currentData(),
            "desktop_path": "",
        }

    def should_create_menu_icon(self):
        return self.finish_page.create_menu_icon_checkbox.isChecked()

    def should_create_desktop_icon(self):
        return self.finish_page.create_desktop_icon_checkbox.isChecked()
