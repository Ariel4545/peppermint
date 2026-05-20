import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk

AUTOSTART_DIR = os.path.expanduser("~/.config/autostart")
AUTOSTART_FILE = os.path.join(AUTOSTART_DIR, "peppermint.desktop")

def is_autostart_enabled():
    if not os.path.exists(AUTOSTART_FILE):
        return False
    try:
        with open(AUTOSTART_FILE, "r") as f:
            content = f.read()
            return "X-GNOME-Autostart-enabled=true" in content
    except Exception:
        return False

def enable_autostart(main_py_path):
    os.makedirs(AUTOSTART_DIR, exist_ok=True)
    executable_path = os.path.abspath(main_py_path)
    desktop_entry = f"""[Desktop Entry]
Type=Application
Exec=python3 {executable_path} --daemon
Hidden=false
NoDisplay=false
Name=Peppermint
Comment=Motivational quotes overlay for Linux Mint (Peppermint Edition)
Icon=preferences-desktop-wallpaper
X-GNOME-Autostart-enabled=true
"""
    try:
        with open(AUTOSTART_FILE, "w") as f:
            f.write(desktop_entry)
        os.chmod(AUTOSTART_FILE, 0o755)
        return True
    except Exception as e:
        print(f"Error creating autostart entry: {e}")
        return False

def disable_autostart():
    if os.path.exists(AUTOSTART_FILE):
        try:
            os.remove(AUTOSTART_FILE)
            return True
        except Exception as e:
            print(f"Error deleting autostart: {e}")
            return False
    return True

def get_monitor_geometries():
    monitors_info = []
    try:
        display = Gdk.Display.get_default()
        if display:
            num_monitors = display.get_n_monitors()
            primary_monitor = display.get_primary_monitor()
            for i in range(num_monitors):
                monitor = display.get_monitor(i)
                geom = monitor.get_geometry()
                name = monitor.get_model() or f"Monitor {i+1}"
                is_primary = (monitor == primary_monitor)
                monitors_info.append({
                    'index': i,
                    'name': name,
                    'x': geom.x,
                    'y': geom.y,
                    'width': geom.width,
                    'height': geom.height,
                    'is_primary': is_primary
                })
    except Exception as e:
        print(f"Error reading monitors info: {e}")
    return monitors_info
