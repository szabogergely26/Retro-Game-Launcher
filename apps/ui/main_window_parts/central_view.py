# Central-view.py
# -----------------

# --- Térkép:

# apps/
# └── ui/
#    ├── main_window.py              # marad a MainWindow osztály központja
#    └── main_window/
#        ├── __init__.py
#        ├── menus.py                # Fájl / Súgó menük
#        ├── toolbar.py              # eszköztár, Új játék gomb
#        ├── statusbar.py            # állapotsor frissítése
#        ├── game_list.py            # lista feltöltése, kijelölés, lista UI
#        └── game_actions.py         # hozzáadás, szerkesztés, törlés, indítás

#     *  ├── central_view            # fő launcher nézet felépítése ( táblázat, gombok, layout)
#        ├──
#        ├──
#        └──




# --- Feladata:

# Retro Game Launcher cím
# Még nincs felvett játék. felirat
# Új játék hozzáadása gomb
# ALT+Enter / exit tipp
# Felvett játékok cím
# játéktáblázat
# Eltávolítás gomb




from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QTableWidget,
    QHeaderView,
    QAbstractItemView,
)

from apps.ui.main_window_parts.game_helpers import game_type_label


def setup_central_view(window):
    """
    A fő launcher nézet létrehozása.
    """

    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    layout.setContentsMargins(32, 32, 32, 32)
    layout.setSpacing(16)

    title_label = QLabel("Retro Game Launcher")
    title_label.setStyleSheet("font-size: 26px; font-weight: bold;")

    window.empty_label = QLabel("Még nincs felvett játék.")
    window.empty_label.setStyleSheet("font-size: 15px;")

    add_button = QPushButton("Új játék hozzáadása")
    add_button.setMinimumHeight(20)
    add_button.setFixedWidth(150)
    add_button.clicked.connect(window._open_add_game_dialog)

    games_title = QLabel("Felvett játékok")
    games_title.setStyleSheet("font-size: 18px; font-weight: bold;")

    fullscreen_hint = QLabel("Teljes képernyő: ALT+Enter")
    fullscreen_hint.setStyleSheet("font-size: 12px;")

    exit_hint = QLabel("Kilépéshez írd be: exit")
    exit_hint.setStyleSheet("font-size: 12px;")

    window.games_table = QTableWidget()
    window.games_table.setColumnCount(3)
    window.games_table.setHorizontalHeaderLabels(["Név", "Típus", "Művelet"])
    window.games_table.setMinimumHeight(220)

    window.games_table.verticalHeader().setVisible(False)
    window.games_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    window.games_table.setSelectionBehavior(QAbstractItemView.SelectRows)
    window.games_table.setSelectionMode(QAbstractItemView.SingleSelection)

    header = window.games_table.horizontalHeader()
    header.setSectionResizeMode(0, QHeaderView.Stretch)
    header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
    header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

    window.games_table.cellDoubleClicked.connect(
        lambda row, _column: window._launch_game_from_row(row)
    )

    window.games_table.itemSelectionChanged.connect(window._update_status_bar)

    window.delete_button = QPushButton("Eltávolítás")
    window.delete_button.setMinimumHeight(20)
    window.delete_button.setFixedWidth(180)
    window.delete_button.clicked.connect(window._delete_selected_game)

    layout.addWidget(title_label)
    layout.addWidget(window.empty_label)

    hint_layout = QVBoxLayout()
    hint_layout.setContentsMargins(80, 0, 0, 0)
    hint_layout.setSpacing(1)
    hint_layout.addWidget(fullscreen_hint)
    hint_layout.addWidget(exit_hint)

    top_layout = QHBoxLayout()
    top_layout.setContentsMargins(0, 0, 0, 0)
    top_layout.setSpacing(12)
    top_layout.addWidget(add_button)
    top_layout.addLayout(hint_layout)
    top_layout.addStretch()

    layout.addLayout(top_layout)

    layout.addWidget(games_title)
    layout.addWidget(window.games_table)
    layout.addWidget(window.delete_button)
    layout.addStretch()

    window.setCentralWidget(central_widget)

    window._reload_games()
