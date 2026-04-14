# 🎬 Rangmanch Player

Rangmanch Player is a premium, high-performance video player built with **Python**, **PyQt6**, and **libmpv**. It combines professional-grade video rendering with a sleek, modern, and high-end aesthetic.

![Rangmanch Player Icon](https://img.icons8.com/fluency/96/movie-projector.png)

## ✨ Features

- **📺 Modern Frameless UI**: A minimalist, dark-themed design with custom title bar and glassmorphism-inspired hover effects.
- **🚀 High Performance**: Powered by the industrial-strength `mpv` engine with hardware acceleration support.
- **🎨 Premium Control Bar**:
  - **Click-to-Seek**: A highly responsive seek bar that allows jumping to any position instantly.
  - **Live Tooltips**: Hover over the seek bar to see the exact timestamp before clicking.
  - **Smart Volume Control**: Integrated mute toggle with visual warnings (red icon) when muted or at zero volume.
- **🎵 Track Management**:
  - **Audio Selector**: Hot-swap between multiple audio tracks/languages during playback.
  - **Subtitle Selector**: Toggle internal subtitles or load external `.srt`, `.ass`, or `.vtt` files on the fly.
- **🔄 Playback Optimization**:
  - **⚡ Speed Controller**: Seamlessly switch playback speed from 0.5x to 2.0x.
  - **Shuffle & Loop**: Multiple shuffle and loop modes (Loop One, Loop All, Off).
  - **Auto-Hide Interface**: Controls fade out gracefully in fullscreen mode.
- **💎 Pro Features**:
  - **🖼️ Thumbnail Preview**: Floating preview window on the seek bar for precise navigation.
  - **🎥 Visual OSD**: Centered high-fidelity icons for volume, seek, and speed feedback.
  - **🖱️ Double-Click Gestures**: Seek forward/backward or toggle fullscreen with simple double-click gestures.
  - **📸 Clean Screenshots**: Dedicated button to capture high-quality frames (excludes UI/OSD automatically).
- **🛠 Advanced Tools**: Built-in Equalizer, Media Information, Video Adjustments, and A-B Loop functionality.

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- `libmpv` (included in the project root)
- Required Python packages:
  ```bash
  pip install PyQt6 python-mpv
  ```

### Running the Player

1.  Navigate to the project root.
2.  Run the main script:
    ```bash
    python main.py
    ```

## ⌨️ Global Shortcuts

| Key | Action |
| --- | --- |
| `Space` | Play / Pause |
| `F` | Toggle Fullscreen |
| `M` | Mute / Unmute |
| `S` | Take Screenshot |
| `Left / Right` | Seek Backward / Forward (10s) |
| `Up / Down` | Volume Up / Down |
| `P / N` | Previous / Next Item |
| `Esc` | Exit Fullscreen |
| **Double-Click Left** | Seek Backward (10s) |
| **Double-Click Right**| Seek Forward (10s) |
| **Double-Click Center**| Toggle Fullscreen |

## 🛠 Project Structure

- `main.py`: Entry point for the application.
- `controls.py`: The core ControlBar widget implementation.
- `mpv_widget.py`: OpenGL-based MPV rendering widget.
- `player_window.py`: Main window management and layout.
- `playlist_panel.py`: Sidebar for managing your media queue.

---
*Created for a superior cinematic experience.*
