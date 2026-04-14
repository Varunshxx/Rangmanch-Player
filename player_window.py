import os
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QMenu
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QAction, QDragEnterEvent, QDropEvent, QCursor

from title_bar import TitleBar
from mpv_widget import MpvWidget
from controls import ControlBar
from playlist_panel import PlaylistPanel
from ab_loop import ABLoop
from themes import MAIN_STYLE
from config import config

from equalizer_dialog import EqualizerDialog
from video_adjustments import VideoAdjustmentsDialog
from media_info_dialog import MediaInfoDialog
from settings_dialog import SettingsDialog

class PlayerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rangmanch Player")
        self.setMinimumSize(1000, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAcceptDrops(True)
        self.setStyleSheet(MAIN_STYLE)

        # Main Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Custom Title Bar
        self.title_bar = TitleBar(self)
        self.main_layout.addWidget(self.title_bar)

        # 2. Content Area (Player + Sidebar)
        self.content_widget = QWidget()
        self.content_layout = QHBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        # Video Player + Controls container
        self.player_container = QWidget()
        self.player_v_layout = QVBoxLayout(self.player_container)
        self.player_v_layout.setContentsMargins(0, 0, 0, 0)
        self.player_v_layout.setSpacing(0)

        self.mpv_widget = MpvWidget(self)
        self.control_bar = ControlBar(self.mpv_widget.player, self)
        
        self.player_v_layout.addWidget(self.mpv_widget, 1)
        self.player_v_layout.addWidget(self.control_bar)
        
        self.content_layout.addWidget(self.player_container, 1)

        # Playlist Sidebar (Hidden by default)
        self.playlist_panel = PlaylistPanel(self)
        self.playlist_panel.setVisible(False)
        self.content_layout.addWidget(self.playlist_panel)

        self.main_layout.addWidget(self.content_widget, 1)

        # 3. Logic & Helpers
        self.ab_loop = ABLoop(self.mpv_widget)
        self._setup_connections()
        self._setup_context_menu()
        
        # Setup Mouse Tracking
        self.mpv_widget.setMouseTracking(True)
        self.setMouseTracking(True)
        self._is_mini = False

    def _setup_connections(self):
        # MPV -> UI
        self.mpv_widget.media_finished.connect(self._on_media_finished)
        
        # UI -> MPV
        self.control_bar.btn_fullscreen.clicked.connect(self._toggle_fullscreen)
        self.control_bar.btn_next.clicked.connect(self.playlist_panel.next_item)
        self.control_bar.btn_prev.clicked.connect(self.playlist_panel.prev_item)
        
        # Playlist -> MPV
        self.playlist_panel.item_selected.connect(self.mpv_widget.load_file)

    def _show_audio_tracks(self):
        self._show_track_menu('audio')

    def _show_subtitle_tracks(self):
        self._show_track_menu('sub')

    def _show_track_menu(self, track_type):
        tracks = self.mpv_widget.player.track_list
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #1a1a1a; color: white; border: 1px solid #4fc3f7; }")
        
        items = [t for t in tracks if t['type'] == track_type]
        
        if track_type == 'sub':
            act = menu.addAction("Disable Subtitles")
            act.triggered.connect(lambda: self.mpv_widget.set_property('sid', 'no'))

        for t in items:
            label = f"{t.get('title') or t.get('lang') or 'Track ' + str(t['id'])}"
            if t['selected']: label = "✓ " + label
            
            act = menu.addAction(label)
            def make_callback(tid=t['id'], tt=track_type):
                return lambda: self.mpv_widget.set_property('aid' if tt=='audio' else 'sid', tid)
            
            act.triggered.connect(make_callback())

        # Show relative to cursor since bar buttons might be gone
        menu.exec(self.mapToGlobal(self.mapFromGlobal(QCursor.pos())))

    def _setup_context_menu(self):
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _show_context_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #1a1a1a; color: white; border: 1px solid #333; } QMenu::item:selected { background-color: #4fc3f7; color: black; }")
        
        menu.addAction("Play/Pause", self.mpv_widget.toggle_pause)
        menu.addAction("Stop", lambda: self.mpv_widget.command('stop'))
        menu.addSeparator()
        
        file_menu = menu.addMenu("File")
        file_menu.addAction("Open File...", self._open_file_dialog)
        file_menu.addAction("Open Folder...", self._open_folder_dialog)
        
        video_menu = menu.addMenu("Video")
        video_menu.addAction("Adjustments...", self._show_adjustments)
        video_menu.addAction("Aspect Ratio", self._cycle_aspect)
        
        audio_menu = menu.addMenu("Audio")
        audio_menu.addAction("Equalizer...", self._show_equalizer)
        
        menu.addSeparator()
        menu.addAction("Media Information", self._show_media_info)
        menu.addAction("Settings", self._show_settings)
        
        menu.exec(self.mapToGlobal(pos))

    def _toggle_playlist(self):
        self.playlist_panel.setVisible(not self.playlist_panel.isVisible())

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.title_bar.show()
            self.control_bar.show_controls()
        else:
            if getattr(self, '_is_mini', False):
                self._toggle_mini_player() # Turn off mini before FS
            self.showFullScreen()
            self.control_bar.show_controls()

    def _toggle_mini_player(self):
        if not hasattr(self, '_is_mini'): self._is_mini = False
        
        if self._is_mini:
            # Back to normal
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            self.resize(1280, 720)
            self._is_mini = False
            self.title_bar.show()
        else:
            # Go Mini
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
            self.resize(320, 180)
            # Move to bottom right corner
            screen = self.screen().availableGeometry()
            self.move(screen.width() - 340, screen.height() - 200)
            self._is_mini = True
            self.title_bar.hide()
            
        self.show() # Re-show to apply flags

    def mouseMoveEvent(self, event):
        # Always show everything when mouse moves
        self.control_bar.show_controls()
        self.title_bar.show()
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseMoveEvent(event)

    def _take_screenshot(self):
        path = config.get("screenshot_path")
        if not os.path.exists(path):
            os.makedirs(path)
        filename = f"screenshot_{int(QTimer.singleShot(0, lambda: 0) or 0)}.png" # simplistic timestamp
        full_path = os.path.join(path, filename)
        self.mpv_widget.command("screenshot-to-file", full_path)

    def _cycle_speed(self):
        speeds = [0.5, 1.0, 1.5, 2.0]
        curr = self.mpv_widget.get_property("speed") or 1.0
        idx = (speeds.index(curr) + 1) % len(speeds) if curr in speeds else 1
        new_speed = speeds[idx]
        self.mpv_widget.set_property("speed", new_speed)

    def _cycle_aspect(self):
        ratios = ["-1", "16:9", "4:3", "2.35:1", "1:1"]
        curr = self.mpv_widget.get_property("video-aspect-override") or "-1"
        idx = (ratios.index(curr) + 1) % len(ratios) if curr in ratios else 0
        new_ratio = ratios[idx]
        self.mpv_widget.set_property("video-aspect-override", new_ratio)

    def _open_file_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Open Media", "", "Video Files (*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm);;All Files (*)")
        if files:
            for f in files:
                self.playlist_panel.add_item(f)
            self.mpv_widget.load_file(files[0])

    def _open_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Folder")
        if folder:
            for root, dirs, files in os.walk(folder):
                for f in files:
                    if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
                        self.playlist_panel.add_item(os.path.join(root, f))

    def _on_media_finished(self):
        if config.get("auto_play_next"):
            self.playlist_panel.next_item()

    # --- Feature Dialogs ---
    def _show_equalizer(self):
        dlg = EqualizerDialog(self.mpv_widget, self)
        dlg.exec()

    def _show_adjustments(self):
        dlg = VideoAdjustmentsDialog(self.mpv_widget, self)
        dlg.exec()

    def _show_media_info(self):
        dlg = MediaInfoDialog(self.mpv_widget, self)
        dlg.exec()

    def _show_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()

    # --- Drag & Drop ---
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        for f in files:
            self.playlist_panel.add_item(f)
        if files:
            self.mpv_widget.load_file(files[0])

    # --- Keyboard Shortcuts ---
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_Space:
            self.mpv_widget.toggle_pause()
        elif key == Qt.Key.Key_F:
            self._toggle_fullscreen()
        elif key == Qt.Key.Key_Escape and self.isFullScreen():
            self._toggle_fullscreen()
        elif key == Qt.Key.Key_Left:
            self.mpv_widget.seek(-10)
        elif key == Qt.Key.Key_Right:
            self.mpv_widget.seek(10)
        elif key == Qt.Key.Key_Up:
            vol = min(150, (self.mpv_widget.get_property('volume') or 0) + 5)
            self.mpv_widget.set_property('volume', vol)
        elif key == Qt.Key.Key_Down:
            vol = max(0, (self.mpv_widget.get_property('volume') or 0) - 5)
            self.mpv_widget.set_property('volume', vol)
        elif key == Qt.Key.Key_M:
            mute = not self.mpv_widget.get_property('mute')
            self.mpv_widget.set_property('mute', mute)
        elif key == Qt.Key.Key_A:
            self._cycle_aspect()
        elif key == Qt.Key.Key_C:
            # Toggle Crop (Panscan)
            current = float(self.mpv_widget.get_property('panscan') or 0.0)
            self.mpv_widget.set_panscan(1.0 if current < 0.5 else 0.0)
        elif key == Qt.Key.Key_S:
            self._take_screenshot()
        elif key == Qt.Key.Key_P:
            self.playlist_panel.prev_item()
        elif key == Qt.Key.Key_N:
            self.playlist_panel.next_item()
        elif key == Qt.Key.Key_I:
            self._toggle_mini_player()
        else:
            super().keyPressEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #1a1a1a; color: white; border: 1px solid #333; } QMenu::item:selected { background-color: #4fc3f7; color: black; }")
        
        # Audio & Subtitles
        audio_menu = menu.addMenu("🎵 Audio tracks")
        self._fill_track_menu(audio_menu, "audio")
        
        sub_menu = menu.addMenu("💬 Subtitles")
        self._fill_track_menu(sub_menu, "sub")

        # Video Menu
        video_menu = menu.addMenu("🎬 Video")
        
        ratio_menu = video_menu.addMenu("Aspect Ratio")
        for r in ["Default", "16:9", "4:3", "2.35:1", "1.85:1"]:
            action = ratio_menu.addAction(r)
            val = "-1" if r == "Default" else r
            action.triggered.connect(lambda chk, v=val: self.mpv_widget.set_aspect_ratio(v))

        zoom_menu = video_menu.addMenu("Zoom / Scale")
        zoom_menu.addAction("Normal (100%)").triggered.connect(lambda: self.mpv_widget.set_property("video-zoom", 0))
        zoom_menu.addAction("Zoom In (120%)").triggered.connect(lambda: self.mpv_widget.set_property("video-zoom", 0.2))
        zoom_menu.addAction("Zoom Out (80%)").triggered.connect(lambda: self.mpv_widget.set_property("video-zoom", -0.2))
        
        crop_action = video_menu.addAction("Toggle Fill (Crop)")
        crop_action.triggered.connect(lambda: self.mpv_widget.set_panscan(1.0 if float(self.mpv_widget.get_property('panscan') or 0.0) < 0.5 else 0.0))

        menu.addSeparator()
        menu.addAction("Take Screenshot (S)", self._take_screenshot)
        menu.addAction("Toggle Fullscreen (F)", self._toggle_fullscreen)
        
        menu.exec(event.globalPos())

    def _fill_track_menu(self, menu, track_type):
        tracks = [t for t in (self.mpv_widget.get_property('track-list') or []) if t['type'] == track_type]
        if not tracks:
            menu.addAction("No tracks").setEnabled(False)
            return
        for t in tracks:
            label = t.get('title') or t.get('lang', 'Unknown')
            action = menu.addAction(f"Track {t['id']}: {label}")
            action.setCheckable(True)
            action.setChecked(t.get('selected', False))
            action.triggered.connect(lambda chk, tid=t['id'], tt=track_type: self.mpv_widget.set_property(tt, tid))
