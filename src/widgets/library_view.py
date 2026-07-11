from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from src.views.models import LibraryItem
from src.widgets.cover import CoverWidget
from src.widgets.flow_layout import FlowLayout


class LibraryView(QScrollArea):
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setObjectName("libraryScroll")

        self._container = QWidget()
        self._flow = FlowLayout(self._container, margin=24, spacing=20)
        self._container.setLayout(self._flow)
        self.setWidget(self._container)

        self._empty_label = QLabel("No comics yet — add a folder to get started")
        self._empty_label.setObjectName("emptyState")
        self._items: dict[int, LibraryItem] = {}
        self._widgets: dict[int, CoverWidget] = {}
        self._search_text = ""
        self._favorites_only = False

        self.favorite_toggled = None
        self.item_clicked = None

    def add_item(self, item: LibraryItem) -> None:
        self._items[item.id] = item
        self._refresh()

    def set_favorite(self, item_id: int, is_favorite: bool) -> None:
        if item_id in self._items:
            self._items[item_id].is_favorite = is_favorite

    def set_search_text(self, text: str) -> None:
        self._search_text = text.lower().strip()
        self._refresh()

    def set_favorites_only(self, enabled: bool) -> None:
        self._favorites_only = enabled
        self._refresh()

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def _visible_items(self) -> list[LibraryItem]:
        items = sorted(self._items.values(), key=lambda i: i.title.lower())
        if self._favorites_only:
            items = [i for i in items if i.is_favorite]
        if self._search_text:
            items = [i for i in items if self._search_text in i.title.lower()]
        return items

    def _refresh(self) -> None:
        while self._flow.count():
            item = self._flow.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        for item in self._visible_items():
            tile = CoverWidget(item.id, item.title, item.cover_path, item.is_favorite)
            tile.favorite_toggled.connect(self._on_favorite_toggled)
            tile.clicked.connect(self._on_item_clicked)
            self._flow.addWidget(tile)

    def _on_favorite_toggled(self, item_id: int, is_favorite: bool) -> None:
        self.set_favorite(item_id, is_favorite)
        if self.favorite_toggled:
            self.favorite_toggled(item_id, is_favorite)

    def _on_item_clicked(self, item_id: int) -> None:
        if self.item_clicked:
            self.item_clicked(item_id)
