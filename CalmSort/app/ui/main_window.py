from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("CalmSort")
        self.resize(1100, 700)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("root")
        layout = QVBoxLayout(root)
        layout.setContentsMargins(48, 42, 48, 42)
        layout.setSpacing(20)

        eyebrow = QLabel("CALMSORT")
        eyebrow.setObjectName("eyebrow")

        title = QLabel("Your workspace, a little calmer.")
        title.setObjectName("title")
        title.setWordWrap(True)

        subtitle = QLabel(
            "A safe, intelligent file organizer that works quietly in the background."
        )
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)

        card = QFrame()
        card.setObjectName("glassCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 28, 28, 28)
        card_layout.setSpacing(12)

        status = QLabel("●  Ready")
        status.setObjectName("status")
        status.setAlignment(Qt.AlignmentFlag.AlignLeft)

        action = QPushButton("Choose a folder")
        action.setObjectName("primaryButton")
        action.setCursor(Qt.CursorShape.PointingHandCursor)

        card_layout.addWidget(status)
        card_layout.addWidget(QLabel("Start by selecting a folder to organize."))
        card_layout.addSpacing(8)
        card_layout.addWidget(action)

        layout.addWidget(eyebrow)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(12)
        layout.addWidget(card)
        layout.addStretch()

        self.setCentralWidget(root)
        self.setStyleSheet(_STYLESHEET)


_STYLESHEET = """
QWidget#root {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #0d1724, stop:0.55 #142438, stop:1 #0b1220);
    color: #eef5ff;
}
QLabel#eyebrow {
    color: #8eb9d8;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 3px;
}
QLabel#title {
    color: #f5f8fc;
    font-size: 36px;
    font-weight: 700;
}
QLabel#subtitle {
    color: #a9b8c8;
    font-size: 16px;
}
QFrame#glassCard {
    background: rgba(255, 255, 255, 18);
    border: 1px solid rgba(255, 255, 255, 34);
    border-radius: 24px;
}
QLabel#status {
    color: #b8e2d0;
    font-size: 15px;
    font-weight: 600;
}
QPushButton#primaryButton {
    background: rgba(142, 185, 216, 45);
    color: #f5f8fc;
    border: 1px solid rgba(180, 220, 245, 80);
    border-radius: 14px;
    padding: 12px 18px;
    font-size: 14px;
    font-weight: 600;
}
QPushButton#primaryButton:hover {
    background: rgba(142, 185, 216, 65);
}
QPushButton#primaryButton:pressed {
    background: rgba(142, 185, 216, 80);
}
"""
