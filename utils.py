import math

def format_time(seconds):
    if seconds is None or math.isnan(seconds):
        return "00:00"
    
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def get_icon_path(icon_name):
    # This will be used to load SVGs from assets/icons
    import os
    return os.path.join(os.path.dirname(__file__), "assets", "icons", icon_name)
