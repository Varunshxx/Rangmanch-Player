from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QFrame
from PyQt6.QtCore import Qt

class VideoAdjustmentsDialog(QDialog):
    """
    Dialog for brightness, contrast, saturation, gamma, and hue.
    """
    def __init__(self, player, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Video Adjustments")
        self.setFixedWidth(300)
        self.player = player
        self.setStyleSheet("background-color: #1a1a1a; color: white;")
        
        layout = QVBoxLayout(self)
        
        self.props = {
            "brightness": (-100, 100, 0),
            "contrast": (-100, 100, 0),
            "saturation": (-100, 100, 0),
            "gamma": (-100, 100, 0),
            "hue": (-100, 100, 0)
        }
        
        for prop, (min_v, max_v, def_v) in self.props.items():
            prop_layout = QVBoxLayout()
            label = QLabel(f"{prop.capitalize()}: 0")
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(min_v, max_v)
            slider.setValue(self.player.get_property(prop) or def_v)
            
            slider.valueChanged.connect(lambda v, p=prop, l=label: self._update_prop(p, v, l))
            
            prop_layout.addWidget(label)
            prop_layout.addWidget(slider)
            layout.addLayout(prop_layout)
            layout.addSpacing(10)

    def _update_prop(self, prop, value, label):
        self.player.set_property(prop, value)
        label.setText(f"{prop.capitalize()}: {value}")
