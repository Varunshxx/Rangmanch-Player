import math
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QSlider, QLabel, QToolTip, QFrame, QGraphicsOpacityEffect,
                             QMenu, QFileDialog)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, pyqtProperty, QEvent, QPoint
from PyQt6.QtGui import QMouseEvent, QCursor
from utils import format_time

class ClickableSlider(QSlider):
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            val = self.minimum() + ((self.maximum() - self.minimum()) * event.position().x()) / self.width()
            self.setValue(int(val))
            self.sliderReleased.emit()
            event.accept()
        super().mousePressEvent(event)

class ControlBar(QWidget):
    def __init__(self, player, parent=None):
        super().__init__(parent)
        self.player = player
        self.setFixedHeight(80)
        self.setObjectName("ControlBar")
        
        self._is_dragging = False
        self._duration = 0
        
        self.setup_ui()
        self.setup_styling()
        self.setup_logic()
        
    def setup_ui(self):
        # Main Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 0, 8, 4)
        self.main_layout.setSpacing(0)
        
        # ROW 1 — Seek Bar
        self.seek_slider = ClickableSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setObjectName("SeekSlider")
        self.seek_slider.setRange(0, 1000)
        self.seek_slider.setMouseTracking(True)
        self.seek_slider.installEventFilter(self)
        self.seek_slider.sliderPressed.connect(self._on_seek_pressed)
        self.seek_slider.sliderReleased.connect(self._on_seek_released)
        
        self.main_layout.addWidget(self.seek_slider)
        
        # ROW 2 — Buttons and Volume
        row2_layout = QHBoxLayout()
        row2_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left side buttons
        self.left_buttons = QHBoxLayout()
        self.left_buttons.setSpacing(4)
        
        self.btn_play = QPushButton("▶")
        self.btn_prev = QPushButton("⏮")
        self.btn_stop = QPushButton("⏹")
        self.btn_next = QPushButton("⏭")
        self.btn_volume_icon = QPushButton("🔊")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setObjectName("VolumeSlider")
        self.volume_slider.setRange(0, 150)
        self.volume_slider.setFixedWidth(100)
        
        for btn in [self.btn_play, self.btn_prev, self.btn_stop, self.btn_next, self.btn_volume_icon]:
            btn.setFixedSize(32, 32)
            btn.setFlat(True)
            self.left_buttons.addWidget(btn)
        
        self.left_buttons.addWidget(self.volume_slider)
        row2_layout.addLayout(self.left_buttons)
        
        row2_layout.addStretch()
        
        # Right side buttons
        self.right_buttons = QHBoxLayout()
        self.right_buttons.setSpacing(8)
        
        self.btn_shuffle = QPushButton("⇄")
        self.btn_shuffle.setFixedSize(32, 32)
        self.btn_shuffle.setFlat(True)
        
        self.btn_loop = QPushButton("→")
        self.btn_loop.setFixedSize(32, 32)
        self.btn_loop.setFlat(True)

        self.btn_audio = QPushButton("🎵 Audio")
        self.btn_audio.setFixedHeight(32)
        self.btn_audio.setFlat(True)
        self.btn_audio.setStyleSheet("padding: 0 8px;")

        self.btn_subtitles = QPushButton("💬 Subtitles")
        self.btn_subtitles.setFixedHeight(32)
        self.btn_subtitles.setFlat(True)
        self.btn_subtitles.setStyleSheet("padding: 0 8px;")

        self.btn_fullscreen = QPushButton("⛶")
        self.btn_fullscreen.setFixedSize(32, 32)
        self.btn_fullscreen.setFlat(True)

        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setObjectName("TimeLabel")
        
        for btn in [self.btn_shuffle, self.btn_loop, self.btn_audio, self.btn_subtitles, self.btn_fullscreen]:
            self.right_buttons.addWidget(btn)
            
        self.right_buttons.addWidget(self.time_label)
        row2_layout.addLayout(self.right_buttons)
        
        self.main_layout.addLayout(row2_layout)
        
    def setup_styling(self):
        self.setStyleSheet("""
            #ControlBar {
                background-color: #1a1a1a;
            }
            QPushButton {
                background-color: transparent;
                color: #ffffff;
                font-size: 16px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
            QPushButton:pressed {
                background-color: #4fc3f7;
            }
            QLabel {
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            #TimeLabel {
                margin-left: 10px;
            }
            
            /* Seek Slider */
            #SeekSlider::groove:horizontal {
                border: none;
                height: 4px;
                background: #444444;
                margin: 2px 0;
            }
            #SeekSlider:hover::groove:horizontal {
                height: 8px;
            }
            #SeekSlider::handle:horizontal {
                background: #4fc3f7;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            #SeekSlider::sub-page:horizontal {
                background: #4fc3f7;
            }
            
            /* Volume Slider */
            #VolumeSlider::groove:horizontal {
                border: none;
                height: 4px;
                background: #444444;
            }
            #VolumeSlider::handle:horizontal {
                background: #4fc3f7;
                width: 10px;
                height: 10px;
                margin: -3px 0;
                border-radius: 5px;
            }
            #VolumeSlider::sub-page:horizontal {
                background: #4fc3f7;
            }

            /* QMenu Styling */
            QMenu {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 4px;
                font-size: 13px;
            }
            QMenu::item:checked {
                color: #4fc3f7;
            }
            QMenu::item:selected {
                background-color: #4fc3f7;
                color: #000000;
            }
            QMenu::item:disabled {
                color: #666666;
            }
            QMenu::separator {
                height: 1px;
                background: #444444;
                margin: 4px 8px;
            }
        """)

    def setup_logic(self):
        # Connections UI -> MPV
        self.btn_play.clicked.connect(self._toggle_pause)
        self.btn_stop.clicked.connect(lambda: self._safe_command('stop'))
        # Buttons next/prev are connected by the parent (PlayerWindow) to the PlaylistPanel
        self.btn_volume_icon.clicked.connect(self._toggle_mute)
        self.volume_slider.valueChanged.connect(self._set_volume)
        self.btn_fullscreen.clicked.connect(self._toggle_fullscreen)
        self.btn_shuffle.clicked.connect(self._toggle_shuffle)
        self.btn_loop.clicked.connect(self._toggle_loop)
        
        self.btn_audio.clicked.connect(self._show_audio_menu)
        self.btn_subtitles.clicked.connect(self._show_subtitle_menu)
        
        # Real time sync via MPV
        self.player.observe_property('time-pos', self.update_time_pos)
        self.player.observe_property('duration', self.update_duration)
        self.player.observe_property('pause', self.update_play_button)
        self.player.observe_property('volume', self.update_volume_slider)
        self.player.observe_property('mute', self.update_mute)
        self.player.observe_property('track-list', self._on_track_list_changed)
        
        # Backup sync timer
        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.sync_ui)
        self.timer.start()
        
        # Auto-hide setup
        self.fade_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.fade_effect)
        self.fade_anim = QPropertyAnimation(self.fade_effect, b"opacity")
        self.fade_anim.setDuration(400)
        
        self.hide_timer = QTimer(self)
        self.hide_timer.setInterval(3000)
        self.hide_timer.timeout.connect(self._on_hide_timeout)

    # --- UI Update Methods (Connected to MPV Properties) ---
    def update_time_pos(self, name, value):
        # Safety check to prevent RuntimeError for deleted C++ objects
        try:
            if value is not None and not self._is_dragging:
                if self._duration > 0:
                    self.seek_slider.setValue(int((value / self._duration) * 1000))
                self._update_time_label(value, self._duration)
        except RuntimeError:
            pass

    def update_duration(self, name, value):
        try:
            if value is not None:
                self._duration = value
                self._update_time_label(self.player.time_pos or 0, value)
        except RuntimeError:
            pass

    def update_play_button(self, name, value):
        try:
            self.btn_play.setText("▶" if value else "⏸")
        except RuntimeError:
            pass

    def update_volume_slider(self, name, value):
        try:
            if value is not None:
                self.volume_slider.blockSignals(True)
                self.volume_slider.setValue(int(value))
                self.volume_slider.blockSignals(False)
                self._refresh_volume_icon()
        except RuntimeError:
            pass

    def update_mute(self, name, value):
        try:
            self._refresh_volume_icon()
        except RuntimeError:
            pass

    def _refresh_volume_icon(self):
        is_muted = self.player.mute
        vol = self.player.volume or 0
        if is_muted or vol == 0:
            self.btn_volume_icon.setText("🔇")
            self.btn_volume_icon.setStyleSheet("color: #ff5252;") # Reddish for mute
        else:
            self.btn_volume_icon.setText("🔊")
            self.btn_volume_icon.setStyleSheet("color: #ffffff;")

    def _on_track_list_changed(self, name, value):
        # We don't need to do much here since we rebuild menus on click,
        # but this property observation ensures MPV is ready.
        pass

    def sync_ui(self):
        try:
            # Backup sync
            pos = self.player.time_pos or 0
            dur = self.player.duration or 0
            self._duration = dur
            if not self._is_dragging and dur > 0:
                self.seek_slider.setValue(int((pos / dur) * 1000))
            self._update_time_label(pos, dur)
            self.update_play_button('pause', self.player.pause)
            self.update_volume_slider('volume', self.player.volume)
            self._refresh_volume_icon()
            self._update_shuffle_button()
            self._update_loop_button()
            self._update_fullscreen_button()
        except RuntimeError:
            pass

    def _update_time_label(self, pos, dur):
        self.time_label.setText(f"{format_time(pos)} / {format_time(dur)}")

    def _safe_command(self, *args):
        try:
            return self.player.command(*args)
        except Exception:
            return None

    def _update_shuffle_button(self):
        shuffle = self.player.shuffle
        self.btn_shuffle.setStyleSheet("background-color: #4fc3f7; border-radius: 6px;" if shuffle else "")

    def _update_loop_button(self):
        loop_playlist = self.player['loop-playlist']
        loop_file = self.player['loop-file']
        if loop_file != 'no':
            self.btn_loop.setText("↺¹")
            self.btn_loop.setStyleSheet("background-color: #4fc3f7; border-radius: 6px;")
        elif loop_playlist != 'no':
            self.btn_loop.setText("↻")
            self.btn_loop.setStyleSheet("background-color: #4fc3f7; border-radius: 6px;")
        else:
            self.btn_loop.setText("→")
            self.btn_loop.setStyleSheet("")

    # --- Actions ---
    def _toggle_pause(self):
        self.player.pause = not self.player.pause

    def _toggle_mute(self):
        self.player.mute = not self.player.mute
        self._refresh_volume_icon()

    def _set_volume(self, value):
        self.player.volume = value
        self._refresh_volume_icon()

    def _on_seek_pressed(self):
        self._is_dragging = True

    def _on_seek_released(self):
        self._is_dragging = False
        val = self.seek_slider.value()
        self.player.seek(val / 10, 'absolute-percent')

    def _toggle_fullscreen(self):
        self.player.fullscreen = not self.player.fullscreen
        self._update_fullscreen_button()

    def _update_fullscreen_button(self):
        is_fs = self.player.fullscreen or (self.window() and self.window().isFullScreen())
        self.btn_fullscreen.setText("⊡" if is_fs else "⛶")
        self.btn_fullscreen.setStyleSheet("background-color: #4fc3f7; border-radius: 6px; color: black;" if is_fs else "")

    def _toggle_shuffle(self):
        self.player.shuffle = not self.player.shuffle
        self._update_shuffle_button()

    def _toggle_loop(self):
        loop_playlist = self.player['loop-playlist']
        loop_file = self.player['loop-file']
        
        if loop_playlist == 'no' and loop_file == 'no':
            self.player['loop-playlist'] = 'inf'
        elif loop_playlist == 'inf':
            self.player['loop-playlist'] = 'no'
            self.player['loop-file'] = 'inf'
        else:
            self.player['loop-file'] = 'no'
            self.player['loop-playlist'] = 'no'
        self._update_loop_button()

    # --- Tracks Menus ---
    def _show_audio_menu(self):
        menu = QMenu(self)
        tracks = self.player.track_list
        audio_tracks = [t for t in tracks if t['type'] == 'audio']
        
        if not audio_tracks:
            act = menu.addAction("No audio tracks")
            act.setEnabled(False)
        else:
            for t in audio_tracks:
                label = f"{t['id']} — {t.get('lang', 'Unknown')}"
                if t.get('title'):
                    label += f" ({t['title']})"
                
                action = menu.addAction(label)
                action.setCheckable(True)
                if t['selected']:
                    action.setChecked(True)
                
                def make_select_audio(tid=t['id']):
                    return lambda: setattr(self.player, 'aid', tid)
                action.triggered.connect(make_select_audio())
        
        pos = self.btn_audio.mapToGlobal(QPoint(0, 0))
        menu.exec(pos - QPoint(0, menu.sizeHint().height()))

    def _show_subtitle_menu(self):
        menu = QMenu(self)
        
        # Off Item
        off_act = menu.addAction("Off")
        off_act.setCheckable(True)
        if not self.player.sid or self.player.sid == 'no':
            off_act.setChecked(True)
        off_act.triggered.connect(lambda: setattr(self.player, 'sid', 'no'))
        
        menu.addSeparator()
        
        tracks = self.player.track_list
        sub_tracks = [t for t in tracks if t['type'] == 'sub']
        
        for t in sub_tracks:
            label = f"{t.get('lang', 'Unknown')}"
            if t.get('title'):
                label += f" ({t['title']})"
            
            action = menu.addAction(label)
            action.setCheckable(True)
            if t['selected']:
                action.setChecked(True)
                
            def make_select_sub(tid=t['id']):
                return lambda: setattr(self.player, 'sid', tid)
            action.triggered.connect(make_select_sub())
            
        menu.addSeparator()
        load_act = menu.addAction("Load subtitle file...")
        load_act.triggered.connect(self._load_subtitle_file)
        
        pos = self.btn_subtitles.mapToGlobal(QPoint(0, 0))
        menu.exec(pos - QPoint(0, menu.sizeHint().height()))

    def _load_subtitle_file(self):
        file_filter = "Subtitle Files (*.srt *.ass *.ssa *.sub *.vtt);;All Files (*)"
        filepath, _ = QFileDialog.getOpenFileName(self, "Load Subtitle File", "", file_filter)
        if filepath:
            self.player.command('sub-add', filepath, 'select')

    # --- Event Filter for Tooltip ---
    def eventFilter(self, obj, event):
        if obj == self.seek_slider and event.type() == QEvent.Type.MouseMove:
            if self._duration > 0:
                pos_x = event.position().x()
                width = self.seek_slider.width()
                percent = max(0, min(1, pos_x / width))
                target_time = percent * self._duration
                QToolTip.showText(event.globalPosition().toPoint(), format_time(target_time), self.seek_slider)
            
            # Reset hide timer on mouse move over slider
            if self.window() and self.window().isFullScreen():
                self.show_controls()
                
        return super().eventFilter(obj, event)

    # --- Auto-Hide Logic ---
    def show_controls(self):
        try:
            # Prevent animation spam during fast state changes
            if self.fade_anim.state() == QPropertyAnimation.State.Running and self.fade_effect.opacity() > 0.5:
                return

            if self.fade_anim.state() == QPropertyAnimation.State.Running:
                self.fade_anim.stop()
            
            self.fade_effect.setOpacity(1.0)
            self.show()
            
            if self.window() and self.window().isFullScreen():
                self.hide_timer.start()
            else:
                self.hide_timer.stop()
        except RuntimeError:
            pass

    def _on_hide_timeout(self):
        try:
            if self.window() and self.window().isFullScreen():
                self.fade_anim.setStartValue(1.0)
                self.fade_anim.setEndValue(0.0)
                self.fade_anim.start()
        except RuntimeError:
            pass

    def mouseMoveEvent(self, event):
        self.show_controls()
        super().mouseMoveEvent(event)
