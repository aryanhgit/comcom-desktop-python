from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QLabel, QPushButton, QVBoxLayout

COVER_WIDTH = 160
COVER_HEIGHT = 230


class CoverWidget(QFrame):
    clicked = Signal(int)
    favorite_toggled = Signal(int, bool)

    def __init__(self, item_id: int, title: str, cover_path: str | None, is_favorite: bool):
        super().__init__()
        self._item_id = item_id
        self._is_favorite = is_favorite

        self.setObjectName("coverTile")
        self.setFixedWidth(COVER_WIDTH)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self._cover_label = QLabel()
        self._cover_label.setObjectName("coverImage")
        self._cover_label.setFixedSize(COVER_WIDTH, COVER_HEIGHT)
        self._cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._set_pixmap(cover_path)

        self._favorite_button = QPushButton("★" if is_favorite else "☆", self._cover_label)
        self._favorite_button.setObjectName("favoriteButton")
        self._favorite_button.setFixedSize(28, 28)
        self._favorite_button.move(COVER_WIDTH - 34, 6)
        self._favorite_button.clicked.connect(self._on_favorite_clicked)

        self._title_label = QLabel(title)
        self._title_label.setObjectName("coverTitle")
        self._title_label.setWordWrap(True)
        self._title_label.setFixedWidth(COVER_WIDTH)

        layout.addWidget(self._cover_label)
        layout.addWidget(self._title_label)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(0)
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        self._shadow = shadow

    def _set_pixmap(self, cover_path: str | None) -> None:
        if cover_path:
            pixmap = QPixmap(cover_path).scaled(
                COVER_WIDTH, COVER_HEIGHT, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation
            )
            self._cover_label.setPixmap(pixmap)
        else:
            self._cover_label.setText("No Cover")

    def _on_favorite_clicked(self) -> None:
        self._is_favorite = not self._is_favorite
        self._favorite_button.setText("★" if self._is_favorite else "☆")
        self.favorite_toggled.emit(self._item_id, self._is_favorite)

    def enterEvent(self, event) -> None:
        self._shadow.setBlurRadius(18)
        self._shadow.setColor(Qt.GlobalColor.black)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._shadow.setBlurRadius(0)
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._item_id)
        super().mouseReleaseEvent(event)
