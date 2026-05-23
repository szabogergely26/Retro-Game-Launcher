"""
Retro Game Launcher - indító készítő űrlap

Ebben a fájlban van a fő adatbeviteli felület:
- játék neve
- indítófájl
- ikon
- játék típusa
- indító létrehozása gomb

A tényleges .desktop fájl generálását később külön core modulba tesszük.
"""

import shutil
import subprocess

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from apps.core.desktop_writer import create_menu_desktop_launcher

class LauncherForm(QWidget):
    """
    A retro játék indító létrehozásához használt űrlap.

    Ez egy külön QWidget, amit a MainWindow fog megjeleníteni.
    Így a főablak tiszta marad, az űrlaplogika pedig itt van egy helyen.
    """

    def __init__(self):
        super().__init__()

        # A külön inicializáló metódus átláthatóbbá teszi a kódot.
        self._build_ui()

    def _build_ui(self):
        """
        Az űrlap vizuális elemeinek létrehozása és elrendezése.
        """

        # Fő függőleges layout az egész űrlapnak.
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(18)

        # Cím.
        title_label = QLabel("Új retro játék indító")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        # Rövid magyarázó szöveg.
        description_label = QLabel(
            "Add meg a játék nevét, indítófájlját és ikonját. "
            "A program később ebből készít egy Linux .desktop indítót."
        )
        description_label.setWordWrap(True)
        description_label.setStyleSheet("font-size: 14px;")

        # Űrlap layout: bal oldalon címkék, jobb oldalon mezők.
        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        # Játék neve.
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Például: Doom, Jazz Jackrabbit, Warcraft II")

        # Indítófájl mező + tallózás gomb.
        self.executable_input = QLineEdit()
        self.executable_input.setPlaceholderText("Játék indítófájlja vagy scriptje")

        self.executable_browse_button = QPushButton("Tallózás...")
        self.executable_browse_button.clicked.connect(self._browse_executable)

        executable_row = QHBoxLayout()
        executable_row.addWidget(self.executable_input)
        executable_row.addWidget(self.executable_browse_button)

        # Ikon mező + tallózás gomb.
        self.icon_input = QLineEdit()
        self.icon_input.setPlaceholderText("Ikonfájl, például .png vagy .svg")

        self.icon_browse_button = QPushButton("Tallózás...")
        self.icon_browse_button.clicked.connect(self._browse_icon)

        icon_row = QHBoxLayout()
        icon_row.addWidget(self.icon_input)
        icon_row.addWidget(self.icon_browse_button)

        # Játék típusa.
        self.type_combo = QComboBox()
        self.type_combo.addItems(
            [
                "Natív / közvetlen indítás",
                "DOSBox",
                "Wine",
                "Egyedi parancs",
            ]
        )

        # Az űrlap sorainak hozzáadása.
        form_layout.addRow("Név:", self.name_input)
        form_layout.addRow("Indítófájl:", executable_row)
        form_layout.addRow("Ikon:", icon_row)
        form_layout.addRow("Típus:", self.type_combo)

        # Létrehozás gomb.
        self.create_button = QPushButton("Indító létrehozása")
        self.create_button.setMinimumHeight(38)
        self.create_button.clicked.connect(self._create_launcher_clicked)

        # Menü frissítése gomb.
        self.refresh_menu_button = QPushButton("Menü frissítése")
        self.refresh_menu_button.setMinimumHeight(38)
        self.refresh_menu_button.clicked.connect(self._refresh_menu_clicked)




        # Egyelőre csak ideiglenes státusz szöveg.
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)

        # Widgetek hozzáadása a fő layouthoz.
        main_layout.addWidget(title_label)
        main_layout.addWidget(description_label)
        main_layout.addSpacing(8)
        main_layout.addLayout(form_layout)
        main_layout.addSpacing(12)
        main_layout.addWidget(self.create_button)
        main_layout.addWidget(self.refresh_menu_button)
        main_layout.addWidget(self.status_label)
        main_layout.addStretch()

    def _browse_executable(self):
        """
        Indítófájl kiválasztása fájlválasztó ablakkal.
        """

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Indítófájl kiválasztása",
            "",
            "Minden fájl (*)",
        )

        # Ha a felhasználó választott fájlt, betesszük a mezőbe.
        if file_path:
            self.executable_input.setText(file_path)

    def _browse_icon(self):
        """
        Ikonfájl kiválasztása fájlválasztó ablakkal.
        """

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Ikon kiválasztása",
            "",
            "Képfájlok (*.png *.svg *.jpg *.jpeg);;Minden fájl (*)",
        )

        # Ha a felhasználó választott fájlt, betesszük a mezőbe.
        if file_path:
            self.icon_input.setText(file_path)

    def _create_launcher_clicked(self):
        """
        Indító létrehozása a Linux alkalmazásmenübe.

        Ez már ténylegesen létrehoz egy .desktop fájlt:
        ~/.local/share/applications/
        """

        name = self.name_input.text().strip()
        executable = self.executable_input.text().strip()
        icon = self.icon_input.text().strip()
        launcher_type = self.type_combo.currentText()

        try:
            desktop_path = create_menu_desktop_launcher(
                name=name,
                executable_path=executable,
                icon_path=icon,
                launcher_type=launcher_type,
            )

        except Exception as error:
            self.status_label.setText(f"Hiba az indító létrehozásakor:\n{error}")
            return

        self.status_label.setText(
            "Indító sikeresen létrehozva.\n\n"
            f"Fájl:\n{desktop_path}\n\n"
            "Ha nem jelenik meg azonnal a menüben, jelentkezz ki/be, "
            "vagy indítsd újra a menüt."
        )



    def _refresh_menu_clicked(self):
        """
        KDE alkalmazásmenü frissítése.

        Plasma 6 alatt a kbuildsycoca6 parancs frissíti az alkalmazásindítók
        gyorsítótárát. Régebbi KDE esetén megpróbáljuk a kbuildsycoca5-öt is.
        """

        command = None

        # Plasma 6 / KDE 6 esetén ez a jó.
        if shutil.which("kbuildsycoca6"):
            command = "kbuildsycoca6"

        # Régebbi KDE / Plasma 5 esetén ez lehet a jó.
        elif shutil.which("kbuildsycoca5"):
            command = "kbuildsycoca5"

        if command is None:
            self.status_label.setText(
                "Nem található KDE menüfrissítő parancs.\n"
                "Próbáld kézzel:\n"
                "update-desktop-database ~/.local/share/applications"
            )
            return

        try:
            result = subprocess.run(
                [command],
                check=False,
                capture_output=True,
                text=True,
            )

        except Exception as error:
            self.status_label.setText(f"Hiba a menü frissítésekor:\n{error}")
            return

        if result.returncode == 0:
            self.status_label.setText(
                f"Menü frissítve ezzel a paranccsal:\n{command}"
            )
            return

        self.status_label.setText(
            "A menüfrissítés lefutott, de hibakóddal tért vissza.\n\n"
            f"Parancs: {command}\n"
            f"Hibakód: {result.returncode}\n"
            f"Hibaüzenet:\n{result.stderr.strip()}"
        )
