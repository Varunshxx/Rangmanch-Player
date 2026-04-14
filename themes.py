MAIN_STYLE = """
QMainWindow {
    background-color: #0a0a0a;
}

QWidget {
    color: #ffffff;
    font-family: 'Segoe UI', sans-serif;
}

/* Custom Title Bar */
#TitleBar {
    background-color: #0d0d0d;
    border-bottom: 1px solid #1a1a1a;
}

/* Control Bar Pill */
#ControlBar {
    background-color: rgba(15, 15, 15, 0.9);
    border: 1px solid rgba(79, 195, 247, 0.4);
    border-radius: 25px;
}

/* Buttons */
QPushButton {
    background: transparent;
    border: none;
    padding: 8px;
    color: white;
    font-size: 14px;
}

QPushButton:hover {
    background-color: rgba(79, 195, 247, 0.1);
    color: #4fc3f7;
}

QPushButton#PlayPauseBtn {
    background-color: #4fc3f7;
    border-radius: 20px;
    min-width: 40px;
    min-height: 40px;
    color: #000000;
}

QPushButton#PlayPauseBtn:hover {
    background-color: #81d4fa;
}

/* Sliders */
QSlider::groove:horizontal {
    border: 1px solid #1a1a1a;
    height: 4px;
    background: #333333;
    margin: 2px 0;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #4fc3f7;
    border: 1px solid #4fc3f7;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}

QSlider::sub-page:horizontal {
    background: #4fc3f7;
    border-radius: 2px;
}

/* Progress/Seek Bar specifically */
#SeekBar::groove:horizontal {
    height: 6px;
}

#SeekBar::handle:horizontal {
    width: 16px;
    height: 16px;
    margin: -5px 0;
}

/* Sidebar */
#PlaylistPanel {
    background-color: #0d0d0d;
    border-left: 1px solid #1a1a1a;
}

QListWidget {
    background-color: transparent;
    border: none;
    outline: none;
}

QListWidget::item {
    padding: 10px;
    border-bottom: 1px solid #1a1a1a;
}

QListWidget::item:selected {
    background-color: rgba(79, 195, 247, 0.2);
    color: #4fc3f7;
    border-left: 3px solid #4fc3f7;
}

/* Tooltips */
QToolTip {
    background-color: #1a1a1a;
    color: #ffffff;
    border: 1px solid #4fc3f7;
    border-radius: 4px;
}
"""
