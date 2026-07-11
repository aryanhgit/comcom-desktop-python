import sys
import os
from PySide6.QtWidgets import QApplication
from src.widgets.window import MainWindow

class App(QApplication):
    pass

def main() -> None:
    pass 

if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open("assets/style.qss", encoding="utf-8") as stylesheet:
        app.setStyleSheet(stylesheet.read())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())