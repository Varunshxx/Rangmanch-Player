from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtCore import Qt

class MediaInfoDialog(QDialog):
    """
    Shows detailed media information.
    """
    def __init__(self, player, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Media Information")
        self.resize(500, 600)
        self.setStyleSheet("background-color: #1a1a1a; color: white;")
        
        layout = QVBoxLayout(self)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet("font-family: Consolas, monospace; background: transparent; border: none;")
        layout.addWidget(self.info_text)
        
        self.refresh_info(player)

    def refresh_info(self, player):
        try:
            # Gather info from MPV properties
            path = player.get_property('path')
            fmt = player.get_property('file-format')
            v_codec = player.get_property('video-codec')
            a_codec = player.get_property('audio-codec')
            res = f"{player.get_property('width')}x{player.get_property('height')}"
            fps = player.get_property('container-fps')
            
            info = f"FILE INFO\n"
            info += f"Path: {path}\n"
            info += f"Format: {fmt}\n\n"
            info += f"VIDEO\n"
            info += f"Codec: {v_codec}\n"
            info += f"Resolution: {res}\n"
            info += f"FPS: {fps:.2f if fps else 'N/A'}\n\n"
            info += f"AUDIO\n"
            info += f"Codec: {a_codec}\n"
            
            self.info_text.setPlainText(info)
        except:
            self.info_text.setPlainText("Failed to retrieve media information.")
