import os
import json
from platformdirs import user_config_dir

class ConfigManager:
    def __init__(self, app_name="Player"):
        self.config_dir = user_config_dir(app_name)
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.recent_file = os.path.join(self.config_dir, "recent.json")
        
        # Default settings
        self.defaults = {
            "hardware_accel": "auto",
            "volume": 80,
            "resume_playback": True,
            "auto_load_subs": True,
            "sub_font_size": 40,
            "sub_color": "#FFFFFF",
            "screenshot_path": os.path.join(os.path.expanduser("~"), "Desktop", "Screenshots"),
            "window_geometry": None,
            "auto_play_next": True,
            "theme": "Dark"
        }
        
        self.settings = self.load_config()
        self._ensure_dirs()

    def _ensure_dirs(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        if not os.path.exists(self.settings["screenshot_path"]):
            try:
                os.makedirs(self.settings["screenshot_path"])
            except:
                pass

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return {**self.defaults, **loaded}
            except:
                return self.defaults.copy()
        return self.defaults.copy()

    def save_config(self):
        self._ensure_dirs()
        with open(self.config_file, 'w') as f:
            json.dump(self.settings, f, indent=4)

    def get_recent_files(self):
        if os.path.exists(self.recent_file):
            try:
                with open(self.recent_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_recent_files(self, files_list):
        self._ensure_dirs()
        with open(self.recent_file, 'w') as f:
            json.dump(files_list[:20], f, indent=4)  # Keep last 20

    def get(self, key):
        return self.settings.get(key, self.defaults.get(key))

    def set(self, key, value):
        self.settings[key] = value
        self.save_config()

config = ConfigManager()
