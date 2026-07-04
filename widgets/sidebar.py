import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QListWidget, QLabel, QLineEdit, QListWidgetItem
)
from PySide6.QtGui import QIcon
import resources_rc

class Sidebar(QWidget):
    """Sidebar Widget: Toggle"""

    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")

        self.sidebar_ = QVBoxLayout(self)   
        self.sidebar_.setContentsMargins(16, 16, 16, 16)
        self.sidebar_.setSpacing(16)
        self.setFixedWidth(240)

        # Search Section
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search")
        self.search_bar.setFixedHeight(32)

        search_icon = QIcon(":/search.svg")
        self.search_action = self.search_bar.addAction(
            search_icon, 
            QLineEdit.ActionPosition.LeadingPosition
        )
        self.search_action.triggered.connect(self._search)
        self.search_bar.returnPressed.connect(self._search)
        self.sidebar_.addWidget(self.search_bar)

        # Library Section 
        self._label("Library")
        self.library = QListWidget()
        self.library.addItem(self._add("Recents", "clock.svg"))
        self.library.addItem(self._add("All", "book.svg"))
        self.library.setMaximumHeight(self.library.sizeHintForRow(0) * self.library.count() + 2
        )
        

        # Collections Section 
        self.collections = QListWidget()
        self.collections.addItem(self._add("Finished", "check.svg"))
        self.collections.addItem(self._add("Reading", "rest.svg"))
        self.collections.addItem(self._add("Paused", "rest.svg"))


        # Section Stacking 
        self.sidebar_.addWidget(self._label("Library"))
        self.sidebar_.addWidget(self.library)
        self.sidebar_.addWidget(self._label("Collections"))
        self.sidebar_.addWidget(self.collections)
        self.sidebar_.addStretch()
        

    def _search(self):
        search_text = self.search_bar.text()
        print(f"Searching for: {search_text}")


    def _label(self, label):
        label = QLabel(label)
        label.setObjectName("section")
        return label
    
    def _add(self, label, svg):
        item = QListWidgetItem(
            QIcon(f":/{svg}"),
            label
        )
        return item


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Sidebar()
    window.show()
    sys.exit(app.exec())
