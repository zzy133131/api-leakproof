"""API LeakProof — Application entry point."""
import sys
import os

# Ensure project root is on path for development runs
_src = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _src not in sys.path:
    sys.path.insert(0, _src)

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor

from app.main_window import MainWindow
from app.styles import Colors, STYLESHEET
from db.models import init_db
from config.settings import APP_NAME


def main():
    # Initialize database
    init_db()

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyleSheet(STYLESHEET)

    # Dark palette for native dialogs
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(Colors.BG_PRIMARY))
    palette.setColor(QPalette.WindowText, QColor(Colors.TEXT_PRIMARY))
    palette.setColor(QPalette.Base, QColor(Colors.BG_TERTIARY))
    palette.setColor(QPalette.Text, QColor(Colors.TEXT_PRIMARY))
    palette.setColor(QPalette.Button, QColor(Colors.BTN_PRIMARY))
    palette.setColor(QPalette.ButtonText, QColor("white"))
    app.setPalette(palette)

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
