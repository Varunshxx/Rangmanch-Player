import sys
import os
from PyQt6.QtWidgets import QApplication
from player_window import PlayerWindow

def main():
    # Performance tweaks for high-DPI displays
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    app = QApplication(sys.argv)
    app.setApplicationName("Video Player")
    app.setOrganizationName("VS")
    
    # Force dark mode palette if needed, but QSS handles most of it
    
    window = PlayerWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
