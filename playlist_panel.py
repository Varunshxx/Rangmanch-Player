from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

class PlaylistPanel(QWidget):
    """
    Sidebar playlist management.
    """
    item_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PlaylistPanel")
        self.setFixedWidth(300)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        header = QHBoxLayout()
        title = QLabel("PLAYLIST")
        title.setStyleSheet("font-weight: bold; color: #4fc3f7;")
        self.btn_clear = QPushButton("Clear")
        self.btn_clear.setFixedWidth(60)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.btn_clear)
        layout.addLayout(header)
        
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.list_widget)
        
        self.items = []

    def add_item(self, path):
        import os
        filename = os.path.basename(path)
        item = QListWidgetItem(filename)
        item.setData(Qt.ItemDataRole.UserRole, path)
        self.list_widget.addItem(item)
        self.items.append(path)

    def _on_item_double_clicked(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        self.item_selected.emit(path)

    def clear(self):
        self.list_widget.clear()
        self.items = []
        
    def next_item(self):
        curr = self.list_widget.currentRow()
        if curr < self.list_widget.count() - 1:
            self.list_widget.setCurrentRow(curr + 1)
            self._on_item_double_clicked(self.list_widget.currentItem())
            
    def prev_item(self):
        curr = self.list_widget.currentRow()
        if curr > 0:
            self.list_widget.setCurrentRow(curr - 1)
            self._on_item_double_clicked(self.list_widget.currentItem())
