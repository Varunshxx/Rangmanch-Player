from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QIcon

class TitleBar(QWidget):
    """
    Custom frameless title bar.
    Handles window dragging and window controls (min/max/close).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self.setFixedHeight(40)
        self.parent = parent
        self._drag_pos = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 5, 0)
        layout.setSpacing(10)

        # App Logo/Name
        self.logo_label = QLabel("RANGMANCH PLAYER")
        self.logo_label.setStyleSheet("font-weight: bold; color: #4fc3f7; letter-spacing: 1px;")
        layout.addWidget(self.logo_label)

        layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        # Window Controls
        self.btn_min = QPushButton("━")
        self.btn_max = QPushButton("▢")
        self.btn_close = QPushButton("✕")
        
        for btn in [self.btn_min, self.btn_max, self.btn_close]:
            btn.setFixedSize(35, 30)
            btn.setStyleSheet("QPushButton:hover { background-color: rgba(255,255,255,0.1); }")
            layout.addWidget(btn)

        self.btn_close.setStyleSheet("QPushButton:hover { background-color: #e81123; color: white; }")

        # Connect slots
        self.btn_min.clicked.connect(self.parent.showMinimized)
        self.btn_max.clicked.connect(self._toggle_max)
        self.btn_close.clicked.connect(self.parent.close)

    def _toggle_max(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.btn_max.setText("▢")
        else:
            self.parent.showMaximized()
            self.btn_max.setText("❐")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.parent.move(self.parent.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event):
        self._toggle_max()
