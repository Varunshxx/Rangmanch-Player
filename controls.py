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
        self._is_vol_dragging = False
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
        self.volume_slider.sliderPressed.connect(self._on_vol_pressed)
        self.volume_slider.sliderReleased.connect(self._on_vol_released)
        
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

        self.btn_speed = QPushButton("⚡ 1.0x")
        self.btn_speed.setFixedHeight(32)
        self.btn_speed.setFlat(True)
        self.btn_speed.setStyleSheet("QPushButton { padding: 0 8px; }")

        self.btn_audio = QPushButton("🎵 Audio")
        self.btn_audio.setFixedHeight(32)
        self.btn_audio.setFlat(True)
        self.btn_audio.setStyleSheet("QPushButton { padding: 0 8px; }")

        self.btn_subtitles = QPushButton("💬 Subtitles")
        self.btn_subtitles.setFixedHeight(32)
        self.btn_subtitles.setFlat(True)
        self.btn_subtitles.setStyleSheet("QPushButton { padding: 0 8px; }")

        self.btn_screenshot = QPushButton("📸")
        self.btn_screenshot.setFixedSize(32, 32)
        self.btn_screenshot.setFlat(True)

        self.btn_fullscreen = QPushButton("⛶")
        self.btn_fullscreen.setFixedSize(32, 32)
        self.btn_fullscreen.setFlat(True)

        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setObjectName("TimeLabel")
        
        for btn in [self.btn_shuffle, self.btn_loop, self.btn_speed, self.btn_audio, self.btn_subtitles, self.btn_screenshot, self.btn_fullscreen]:
            self.right_buttons.addWidget(btn)
        
        # Thumbnail Preview Frame (Floating)
        p = self.window() or self.parent() or self
        self.thumbnail_preview = QFrame(p)
        self.thumbnail_preview.setFixedSize(160, 90)
        self.thumbnail_preview.setObjectName("ThumbnailPreview")
        self.thumbnail_preview.setStyleSheet("""
            #ThumbnailPreview {
                background-color: #000;
                border: 2px solid #4fc3f7;
                border-radius: 4px;
            }
        """)
        self.thumb_label = QLabel(self.thumbnail_preview)
        self.thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumb_label.setScaledContents(True)
        self.thumb_label.setFixedSize(160, 90)
        self.thumbnail_preview.hide()
            
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
            QPushButton[active="true"] {
                background-color: #4fc3f7;
                color: #000000;
            }
            QPushButton[muted="true"] {
                color: #ff5252;
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
        
        self.btn_speed.clicked.connect(self._show_speed_menu)
        self.btn_audio.clicked.connect(self._show_audio_menu)
        self.btn_subtitles.clicked.connect(self._show_subtitle_menu)
        self.btn_screenshot.clicked.connect(self._take_screenshot)
        
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
            if value is not None and not self._is_vol_dragging:
                self.volume_slider.blockSignals(True)
                # Keep real volume in player, but UI shows 0 if muted
                display_val = 0 if self.player.mute else int(value)
                self.volume_slider.setValue(display_val)
                self.volume_slider.blockSignals(False)
                self._refresh_volume_icon()
        except RuntimeError:
            pass

    def update_mute(self, name, value):
        try:
            self.volume_slider.blockSignals(True)
            if value:
                self.volume_slider.setValue(0)
            else:
                self.volume_slider.setValue(int(self.player.volume or 0))
            self.volume_slider.blockSignals(False)
            self._refresh_volume_icon()
        except RuntimeError:
            pass

    def _refresh_volume_icon(self):
        try:
            is_muted = self.player.mute or (self.player.volume == 0)
            self.btn_volume_icon.setText("🔇" if is_muted else "🔊")
            self.btn_volume_icon.setProperty("muted", "true" if self.player.mute else "false")
            self._update_style(self.btn_volume_icon)
        except (RuntimeError, AttributeError):
            pass

    def _update_style(self, widget):
        try:
            if widget and widget.style():
                widget.style().unpolish(widget)
                widget.style().polish(widget)
        except Exception:
            pass

    def _on_track_list_changed(self, name, value):
        # We don't need to do much here since we rebuild menus on click,
        # but this property observation ensures MPV is ready.
        pass

    def sync_ui(self):
        try:
            if not self or not self.player:
                return
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
            self._update_speed_button()
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
        self.btn_shuffle.setProperty("active", "true" if shuffle else "false")
        self.btn_shuffle.style().unpolish(self.btn_shuffle)
        self.btn_shuffle.style().polish(self.btn_shuffle)

    def _update_loop_button(self):
        loop_playlist = self.player['loop-playlist']
        loop_file = self.player['loop-file']
        is_active = False
        if loop_file != 'no':
            self.btn_loop.setText("↺¹")
            is_active = True
        elif loop_playlist != 'no':
            self.btn_loop.setText("↻")
            is_active = True
        else:
            self.btn_loop.setText("→")
            
        self.btn_loop.setProperty("active", "true" if is_active else "false")
        self.btn_loop.style().unpolish(self.btn_loop)
        self.btn_loop.style().polish(self.btn_loop)

    # --- Actions ---
    def _show_speed_menu(self):
        menu = QMenu(self)
        speeds = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
        current_speed = self.player.speed or 1.0
        
        for s in speeds:
            action = menu.addAction(f"{s}x")
            action.setCheckable(True)
            if abs(s - current_speed) < 0.01:
                action.setChecked(True)
            action.triggered.connect(lambda chk, val=s: self._on_speed_changed(val))
            
        pos = self.btn_speed.mapToGlobal(QPoint(0, 0))
        menu.exec(pos - QPoint(0, menu.sizeHint().height()))

    def _on_speed_changed(self, speed):
        self.player.speed = speed
        self._update_speed_button()
        if hasattr(self.parent(), 'show_osd'):
            self.parent().show_osd(f"⚡ Speed: {speed}x")

    def _take_screenshot(self):
        shot_dir = os.path.join(os.path.expanduser("~"), "Pictures", "RangmanchPlayer")
        if not os.path.exists(shot_dir):
            os.makedirs(shot_dir)
        
        filename = f"Snapshot_{int(self.player.time_pos or 0)}s.png"
        path = os.path.join(shot_dir, filename)
        
        # Use 'video' flag to exclude any UI/subtitles overlay if possible
        self.player.command('screenshot-to-file', path, 'video') 
        
        if hasattr(self.parent(), 'show_osd'):
            self.parent().show_osd("📸 Snapshot Saved!")
        else:
            QToolTip.showText(QCursor.pos(), "Snapshot Saved to Pictures!")

    def _toggle_pause(self):
        self.player.pause = not self.player.pause

    def _toggle_mute(self):
        self.player.mute = not self.player.mute
        self._refresh_volume_icon()

    def _set_volume(self, value):
        try:
            # Auto-unmute when user manually changes volume slider
            if self.player.mute and value > 0:
                self.player.mute = False
            
            self.player.volume = value
            self._refresh_volume_icon()
            
            # Visual feedback (only during drag to avoid sync spam)
            if self._is_vol_dragging and hasattr(self.parent(), 'show_osd'):
                self.parent().show_osd(f"🔊 {int(value)}%")
        except RuntimeError:
            pass

    def _on_vol_pressed(self):
        self._is_vol_dragging = True

    def _on_vol_released(self):
        self._is_vol_dragging = False

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
        self.btn_fullscreen.setProperty("active", "true" if is_fs else "false")
        self.btn_fullscreen.style().unpolish(self.btn_fullscreen)
        self.btn_fullscreen.style().polish(self.btn_fullscreen)

    def _update_speed_button(self):
        speed = self.player.speed or 1.0
        self.btn_speed.setText(f"⚡ {speed}x")
        self.btn_speed.setProperty("active", "true" if speed != 1.0 else "false")
        self.btn_speed.style().unpolish(self.btn_speed)
        self.btn_speed.style().polish(self.btn_speed)

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

                # Thumbnail Preview Positioning
                thumb_x = event.position().x() - (self.thumbnail_preview.width() / 2)
                thumb_x = max(0, min(self.seek_slider.width() - self.thumbnail_preview.width(), thumb_x))
                global_pos = self.seek_slider.mapToGlobal(QPoint(int(thumb_x), -self.thumbnail_preview.height() - 10))
                if self.parent():
                    local_pos = self.parent().mapFromGlobal(global_pos)
                    self.thumbnail_preview.move(local_pos)
                    self.thumbnail_preview.show()
            
            # Reset hide timer on mouse move over slider
            if self.window() and self.window().isFullScreen():
                self.show_controls()
        
        elif obj == self.seek_slider and event.type() == QEvent.Type.Leave:
            self.thumbnail_preview.hide()
                
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
