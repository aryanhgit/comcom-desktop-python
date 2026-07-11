from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.views import config
from src.views.database import Database
from src.services.scanner import LibraryScanner
from src.services.thumbnail import ThumbnailService
from src.widgets.library_view import LibraryView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Comics")
        self.resize(1000, 700)

        self._db = Database(config.db_path())
        self._thumbnails = ThumbnailService(config.cache_dir())
        self._scanner = LibraryScanner(self._db, self._thumbnails)
        self._scanner.item_found.connect(self._on_item_found)
        self._scanner.finished.connect(self._on_scan_finished)

        self._favorites_active = False

        central = QWidget()
        central.setObjectName("centralWidget")
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._build_top_bar())
        root_layout.addWidget(self._build_favorites_bar())

        self._library_view = LibraryView()
        self._library_view.favorite_toggled = self._on_favorite_toggled
        self._library_view.item_clicked = self._on_item_clicked
        root_layout.addWidget(self._library_view)

        self.setCentralWidget(central)
        self._load_existing_library()

    def _build_top_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("topBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(24, 16, 24, 16)

        self._search_field = QLineEdit()
        self._search_field.setPlaceholderText("Search")
        self._search_field.setObjectName("searchField")
        self._search_field.textChanged.connect(self._library_view_search)

        add_button = QPushButton("Add Folder")
        add_button.setObjectName("addFolderButton")
        add_button.clicked.connect(self._add_folder)

        settings_button = QPushButton("⚙")
        settings_button.setObjectName("settingsButton")
        settings_button.setFixedWidth(36)

        layout.addWidget(self._search_field)
        layout.addWidget(add_button)
        layout.addWidget(settings_button)
        return bar

    def _build_favorites_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("favoritesBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(24, 0, 24, 12)

        self._favorites_button = QPushButton("★ Favorites")
        self._favorites_button.setObjectName("favoritesToggle")
        self._favorites_button.setCheckable(True)
        self._favorites_button.clicked.connect(self._toggle_favorites)

        layout.addWidget(self._favorites_button)
        layout.addStretch()
        return bar

    def _library_view_search(self, text: str) -> None:
        self._library_view.set_search_text(text)

    def _toggle_favorites(self, checked: bool) -> None:
        self._favorites_active = checked
        self._library_view.set_favorites_only(checked)

    def _add_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Comics Folder")
        if not folder:
            return
        self._db.add_library_folder(folder)
        self._run_scan()

    def _load_existing_library(self) -> None:
        for item in self._db.get_all_items():
            self._library_view.add_item(item)
        if self._db.get_library_folders():
            self._run_scan()

    def _run_scan(self) -> None:
        folders = self._db.get_library_folders()
        self._scanner.scan(folders)

    def _on_item_found(self, item) -> None:
        self._library_view.add_item(item)

    def _on_scan_finished(self) -> None:
        pass

    def _on_favorite_toggled(self, item_id: int, is_favorite: bool) -> None:
        self._db.set_favorite(item_id, is_favorite)

    def _on_item_clicked(self, item_id: int) -> None:
        pass
