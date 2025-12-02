from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication

from .main_window import MainWindow
from .logging_config import init_logging


def main() -> None:
    """Application entry point for the GUI app."""
    # Basic Qt application bootstrap
    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName("PDF Split")
    QCoreApplication.setApplicationName("PDF Split")
    init_logging("PDF Split")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
