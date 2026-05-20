import os
import json

CONFIG_DIR = os.path.expanduser("~/.config/peppermint")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_QUOTES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "quotes")
DEFAULT_QUOTE_FILE = os.path.join(DEFAULT_QUOTES_DIR, "motivational.txt")

DEFAULT_CONFIG = {
    "active_quote_file": DEFAULT_QUOTE_FILE,
    "shuffle": False,
    "autostart": False,
    "run_in_tray": True,
    "monitor_index": -1,
    "font_desc": "Sans Bold 24",
    "text_color": [1.0, 1.0, 1.0, 0.95],
    "alignment": "center",
    "show_shadow": True,
    "shadow_color": [0.0, 0.0, 0.0, 0.6],
    "shadow_offset_x": 2.0,
    "shadow_offset_y": 2.0,
    "show_card": True,
    "card_color": [0.0, 0.0, 0.0, 0.35],
    "card_border_color": [1.0, 1.0, 1.0, 0.15],
    "card_border_width": 1.0,
    "card_corner_radius": 16.0,
    "card_padding": 24.0,
    "max_width_pct": 60,
    "position_preset": "Bottom Center",
    "custom_x_pct": 50.0,
    "custom_y_pct": 80.0,
    "animation_style": "typewriter",
    "typing_speed_ms": 60,
    "delay_completed_sec": 6.0,
    "fade_out_sec": 0.8,
    "delay_next_sec": 1.5
}

class ConfigManager:
    def __init__(self, config_path=CONFIG_PATH):
        self.config_path = config_path
        self.config = DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        if not os.path.exists(self.config_path):
            self.save()
            return
        try:
            with open(self.config_path, "r") as f:
                loaded = json.load(f)
                for k, v in loaded.items():
                    if k in self.config:
                        self.config[k] = v
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")

    def save(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key):
        return self.config.get(key, DEFAULT_CONFIG.get(key))

    def set(self, key, value):
        if key in self.config and self.config[key] != value:
            self.config[key] = value
            self.save()
