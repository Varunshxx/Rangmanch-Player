from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QComboBox, QPushButton, QFileDialog
from PyQt6.QtCore import Qt
from config import config

class SettingsDialog(QDialog):
    """
    Global settings dialog.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedWidth(400)
        self.setObjectName("SettingsDialog")
        
        layout = QVBoxLayout(self)
        
        # HW Accel
        hw_layout = QHBoxLayout()
        hw_layout.addWidget(QLabel("Hardware Acceleration:"))
        self.hw_combo = QComboBox()
        self.hw_combo.addItems(["auto", "auto-safe", "no"])
        self.hw_combo.setCurrentText(config.get("hardware_accel"))
        hw_layout.addWidget(self.hw_combo)
        layout.addLayout(hw_layout)
        
        # Resume Playback
        self.chk_resume = QCheckBox("Resume playback from last position")
        self.chk_resume.setChecked(config.get("resume_playback"))
        layout.addWidget(self.chk_resume)
        
        # Auto-play Next
        self.chk_next = QCheckBox("Auto-play next file in playlist")
        self.chk_next.setChecked(config.get("auto_play_next"))
        layout.addWidget(self.chk_next)
        
        # Screenshot Path
        ss_layout = QVBoxLayout()
        ss_layout.addWidget(QLabel("Screenshot Folder:"))
        ss_path_row = QHBoxLayout()
        self.lbl_ss_path = QLabel(config.get("screenshot_path"))
        self.lbl_ss_path.setWordWrap(True)
        btn_browse = QPushButton("Browse")
        btn_browse.clicked.connect(self._browse_path)
        ss_path_row.addWidget(self.lbl_ss_path, 1)
        ss_path_row.addWidget(btn_browse)
        ss_layout.addLayout(ss_path_row)
        layout.addLayout(ss_layout)
        
        layout.addStretch()
        
        # Save/Cancel
        btns = QHBoxLayout()
        btn_save = QPushButton("Save Settings")
        btn_save.clicked.connect(self._save)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_save)
        btns.addWidget(btn_cancel)
        layout.addLayout(btns)

    def _browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder", self.lbl_ss_path.text())
        if path:
            self.lbl_ss_path.setText(path)

    def _save(self):
        config.set("hardware_accel", self.hw_combo.currentText())
        config.set("resume_playback", self.chk_resume.isChecked())
        config.set("auto_play_next", self.chk_next.isChecked())
        config.set("screenshot_path", self.lbl_ss_path.text())
        self.accept()
