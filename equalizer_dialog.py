from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QPushButton, QComboBox
from PyQt6.QtCore import Qt

class EqualizerDialog(QDialog):
    """
    10-band equalizer dialog.
    """
    def __init__(self, player, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Equalizer")
        self.setFixedWidth(500)
        self.player = player
        self.setObjectName("EqualizerDialog")
        self.setStyleSheet("background-color: #1a1a1a; color: white;")
        
        layout = QVBoxLayout(self)
        
        bands_layout = QHBoxLayout()
        self.bands = [31, 62, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
        self.sliders = []
        
        for freq in self.bands:
            v_layout = QVBoxLayout()
            label = QLabel(f"{freq if freq < 1000 else str(freq//1000)+'k'}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-size: 9px;")
            
            slider = QSlider(Qt.Orientation.Vertical)
            slider.setRange(-20, 20)
            slider.setValue(0)
            slider.setFixedHeight(150)
            slider.valueChanged.connect(self._apply_eq)
            
            v_layout.addWidget(label)
            v_layout.addWidget(slider)
            bands_layout.addLayout(v_layout)
            self.sliders.append(slider)
            
        layout.addLayout(bands_layout)
        
        # Presets
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Preset:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["Flat", "Bass Boost", "Treble Boost", "Cinema", "Music"])
        self.preset_combo.currentIndexChanged.connect(self._on_preset_changed)
        preset_layout.addWidget(self.preset_combo)
        
        btn_reset = QPushButton("Reset")
        btn_reset.clicked.connect(self._reset)
        preset_layout.addWidget(btn_reset)
        
        layout.addLayout(preset_layout)

    def _apply_eq(self):
        # MPV uses af=equalizer=f=31:g=0:f=62:g=0...
        eq_str = "equalizer="
        parts = []
        for i, freq in enumerate(self.bands):
            gain = self.sliders[i].value()
            parts.append(f"f={freq}:g={gain}")
        
        full_str = eq_str + ":".join(parts)
        # Apply filter
        self.player.command("af", "set", full_str)

    def _on_preset_changed(self, index):
        presets = {
            "Flat": [0]*10,
            "Bass Boost": [10, 8, 6, 2, 0, 0, 0, 0, 0, 0],
            "Treble Boost": [0, 0, 0, 0, 0, 2, 6, 8, 10, 10],
            "Cinema": [4, 2, 0, 0, 0, 0, 0, 2, 4, 4],
            "Music": [6, 4, 2, 0, 0, 0, 2, 4, 6, 6]
        }
        vals = presets[self.preset_combo.currentText()]
        for i, v in enumerate(vals):
            self.sliders[i].setValue(v)
        self._apply_eq()

    def _reset(self):
        for s in self.sliders:
            s.setValue(0)
        self._apply_eq()
