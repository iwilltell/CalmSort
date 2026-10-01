import sys

from PySide6.QtWidgets import QApplication

from app.core.logging_config import configure_logging
from app.ui.main_window import MainWindow


def main() -> int:
    configure_logging()
    app = QApplication(sys.argv)
    app.setApplicationName("CalmSort")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
