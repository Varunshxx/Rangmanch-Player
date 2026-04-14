import os
import sys
from PyQt6.QtWidgets import QWidget
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QColor

# Add current directory to path for mpv-2.dll on Windows
if sys.platform == 'win32':
    os.environ['PATH'] = os.path.dirname(__file__) + os.pathsep + os.environ['PATH']

import mpv

class MpvWidget(QOpenGLWidget):
    position_changed = pyqtSignal(float)
    duration_changed = pyqtSignal(float)
    pause_changed = pyqtSignal(bool)
    volume_changed = pyqtSignal(float)
    file_loaded = pyqtSignal(str)
    media_finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.ctx = None
        
        self.player = mpv.MPV(
            vo='libmpv', 
            hwdec='d3d11va', # High performance
            log_handler=print,
            loglevel='info',
            keep_open='yes',
            idle='yes'
        )

        self.player.observe_property('time-pos', self._on_time_pos)
        self.player.observe_property('duration', self._on_duration)
        self.player.observe_property('pause', self._on_pause)
        self.player.observe_property('volume', self._on_volume)
        self.player.observe_property('filename', self._on_filename)
        
        @self.player.event_callback('end-file')
        def on_end_file(event):
            self.media_finished.emit()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_pause()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # Forward mouse movement to the parent window so it can show controls
        window = self.window()
        if window:
            window.mouseMoveEvent(event)
        super().mouseMoveEvent(event)

    def _on_time_pos(self, name, value):
        if value is not None: self.position_changed.emit(value)
    def _on_duration(self, name, value):
        if value is not None: self.duration_changed.emit(value)
    def _on_pause(self, name, value):
        self.pause_changed.emit(value)
    def _on_volume(self, name, value):
        if value is not None: self.volume_changed.emit(value)
    def _on_filename(self, name, value):
        if value: self.file_loaded.emit(value)

    def load_file(self, path):
        self.player.play(path)

    def toggle_pause(self):
        self.player.pause = not self.player.pause

    def set_aspect_ratio(self, ratio):
        # ratio can be "16:9", "4:3", "-1" (reset)
        self.player['video-aspect-override'] = ratio

    def set_panscan(self, value):
        # 0.0 to 1.0 (zoom to fill)
        self.player.panscan = value

    def seek(self, seconds, mode='relative'):
        self.player.seek(seconds, mode)

    def set_property(self, name, value):
        self.player[name] = value

    def get_property(self, name):
        try:
            return getattr(self.player, name.replace('-', '_'), None) or self.player[name]
        except:
            return None

    def command(self, *args):
        try:
            return self.player.command(*args)
        except:
            return None

    def initializeGL(self):
        from ctypes import CFUNCTYPE, c_char_p, c_void_p
        
        # This is the 'handshake' Python needs to talk to the video engine
        PROC_TYPE = CFUNCTYPE(c_void_p, c_void_p, c_char_p)
        
        get_proc_address_raw = None
        if sys.platform == 'win32':
            import ctypes
            wgl = ctypes.WinDLL('opengl32')
            wglGetProcAddress = wgl.wglGetProcAddress
            wglGetProcAddress.argtypes = [c_char_p]
            wglGetProcAddress.restype = c_void_p
            
            def get_proc_address_impl(_, name):
                addr = wglGetProcAddress(name)
                if not addr:
                    # Fallback to standard GL functions
                    addr = ctypes.cast(getattr(wgl, name.decode(), 0), c_void_p).value
                return addr
            
            get_proc_address_raw = PROC_TYPE(get_proc_address_impl)
        
        self.ctx = mpv.MpvRenderContext(self.player, 'opengl', 
                                       opengl_init_params={'get_proc_address': get_proc_address_raw})
        self.ctx.update_cb = self._on_update

    def _on_update(self):
        QTimer.singleShot(0, self.update)

    def paintGL(self):
        if self.ctx:
            # Use the correct 'opengl_fbo' parameter format
            ww = int(self.width() * self.devicePixelRatio())
            hh = int(self.height() * self.devicePixelRatio())
            
            self.ctx.render(
                flip_y=True, 
                opengl_fbo={'fbo': self.defaultFramebufferObject(), 'w': ww, 'h': hh}
            )

    def shutdown(self):
        self.player.terminate()
