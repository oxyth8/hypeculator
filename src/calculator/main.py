"""Application entry point."""

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from .ui import APP_ICON_PATH, APP_NAME, CalculatorWindow


def main() -> int:
    """Start the Calculator desktop application."""
    application = QApplication(sys.argv)
    application.setApplicationName(APP_NAME)
    application.setApplicationDisplayName(APP_NAME)
    application.setDesktopFileName("hypeculator")
    application.setWindowIcon(QIcon(str(APP_ICON_PATH)))
    window = CalculatorWindow()
    window.show()
    return application.exec()
