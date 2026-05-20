import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import os

from peppermint.utils import (
    is_autostart_enabled, enable_autostart, disable_autostart, get_monitor_geometries
)

class SettingsDashboard(Gtk.Window):
    def __init__(self, config_manager, quotes_manager, main_py_path, app=None):
        super().__init__(title="Peppermint - Settings")
        self.config_manager = config_manager
        self.quotes_manager = quotes_manager
        self.main_py_path = main_py_path
        self.app = app

        self.set_default_size(600, 520)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.apply_custom_css()

        # Notebook layout
        notebook = Gtk.Notebook()
        self.add(notebook)

        # Tab 1: General & Position
        tab1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        tab1.set_border_width(15)
        self.build_general_tab(tab1)
        notebook.append_page(tab1, Gtk.Label(label="General & Position"))

        # Tab 2: Style & Backdrop
        tab2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        tab2.set_border_width(15)
        self.build_style_tab(tab2)
        notebook.append_page(tab2, Gtk.Label(label="Style & Backdrop"))

        # Tab 3: Animations & Speeds
        tab3 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        tab3.set_border_width(15)
        self.build_animations_tab(tab3)
        notebook.append_page(tab3, Gtk.Label(label="Animations"))

        # Fill values into UI
        self.load_settings_into_ui()
        self.connect("delete-event", self.on_close)

    def apply_custom_css(self):
        css_provider = Gtk.CssProvider()
        css = """
        window {
            background-color: #2c2c2c;
            color: #ffffff;
        }
        notebook {
            background-color: #2c2c2c;
            border: none;
        }
        notebook tab {
            background-color: #3d3d3d;
            color: #b0b0b0;
            padding: 8px 16px;
            font-weight: bold;
        }
        notebook tab:active {
            background-color: #0288d1;
            color: #ffffff;
        }
        label {
            color: #ffffff;
        }
        button {
            background-color: #3d3d3d;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 6px 12px;
        }
        button:hover {
            background-color: #4d4d4d;
        }
        .primary-btn {
            background-color: #0288d1;
            font-weight: bold;
        }
        .primary-btn:hover {
            background-color: #0277bd;
        }
        """
        try:
            css_provider.load_from_data(css.encode())
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        except Exception as e:
            print(f"Error loading CSS: {e}")

    def update_config(self, key, value):
        self.config_manager.set(key, value)
        if self.app and self.app.overlay:
            if key == "active_quote_file":
                self.quotes_manager.set_active_file(value)
                self.app.overlay.trigger_next_quote()
            elif key == "shuffle":
                self.quotes_manager.set_shuffle(value)
            elif key in ["monitor_index", "position_preset", "custom_x_pct", "custom_y_pct", "max_width_pct"]:
                self.app.overlay.update_geometry()
            else:
                self.app.overlay.queue_draw()

    # --- UI Builders ---

    def build_general_tab(self, box):
        grid = Gtk.Grid(column_spacing=12, row_spacing=12)
        box.pack_start(grid, True, True, 0)

        # Quotes Preset selector
        grid.attach(Gtk.Label(label="Quotes Database:", xalign=0), 0, 0, 1, 1)
        self.preset_combo = Gtk.ComboBoxText()
        self.preset_combo.append("motivational", "Motivational Quotes")
        self.preset_combo.append("zen", "Zen Proverbs")
        self.preset_combo.append("programming", "Programming Sayings")
        self.preset_combo.append("custom", "Custom Quote File...")
        self.preset_combo.connect("changed", self.on_preset_changed)
        grid.attach(self.preset_combo, 1, 0, 1, 1)

        # Custom File Selection
        self.file_chooser_btn = Gtk.FileChooserButton(title="Select Custom Quotes File", action=Gtk.FileChooserAction.OPEN)
        self.file_chooser_btn.connect("file-set", self.on_custom_file_set)
        grid.attach(self.file_chooser_btn, 1, 1, 1, 1)

        # Shuffle
        self.shuffle_chk = Gtk.CheckButton(label="Shuffle Sentences Order")
        self.shuffle_chk.connect("toggled", lambda w: self.update_config("shuffle", w.get_active()))
        grid.attach(self.shuffle_chk, 0, 2, 2, 1)

        # Autostart
        self.autostart_chk = Gtk.CheckButton(label="Autostart on Desktop Login")
        self.autostart_chk.connect("toggled", self.on_autostart_toggled)
        grid.attach(self.autostart_chk, 0, 3, 2, 1)

        # Display target
        grid.attach(Gtk.Label(label="Monitor Target:", xalign=0), 0, 4, 1, 1)
        self.monitor_combo = Gtk.ComboBoxText()
        self.monitor_combo.append("-1", "Primary Monitor")
        for m in get_monitor_geometries():
            self.monitor_combo.append(str(m['index']), f"Monitor {m['index'] + 1} ({m['width']}x{m['height']})")
        self.monitor_combo.connect("changed", lambda w: self.update_config("monitor_index", int(w.get_active_id() or -1)))
        grid.attach(self.monitor_combo, 1, 4, 1, 1)

        # Position Preset
        grid.attach(Gtk.Label(label="Screen Position:", xalign=0), 0, 5, 1, 1)
        self.pos_combo = Gtk.ComboBoxText()
        for p in ["Top Left", "Top Center", "Top Right", "Middle Left", "Center", "Middle Right", "Bottom Left", "Bottom Center", "Bottom Right", "Custom"]:
            self.pos_combo.append(p, p)
        self.pos_combo.connect("changed", self.on_pos_changed)
        grid.attach(self.pos_combo, 1, 5, 1, 1)

        # Custom coordinates box
        self.custom_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        grid.attach(self.custom_box, 0, 6, 2, 1)

        cx_box = Gtk.Box(spacing=10)
        cx_box.pack_start(Gtk.Label(label="Custom X (%):", xalign=0), False, False, 0)
        self.x_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.x_scale.connect("value-changed", lambda w: self.update_config("custom_x_pct", w.get_value()))
        cx_box.pack_start(self.x_scale, True, True, 0)
        self.custom_box.pack_start(cx_box, False, False, 0)

        cy_box = Gtk.Box(spacing=10)
        cy_box.pack_start(Gtk.Label(label="Custom Y (%):", xalign=0), False, False, 0)
        self.y_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.y_scale.connect("value-changed", lambda w: self.update_config("custom_y_pct", w.get_value()))
        cy_box.pack_start(self.y_scale, True, True, 0)
        self.custom_box.pack_start(cy_box, False, False, 0)

        # Max width
        grid.attach(Gtk.Label(label="Max Width (% of Screen):", xalign=0), 0, 7, 1, 1)
        self.width_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 20, 100, 5)
        self.width_scale.connect("value-changed", lambda w: self.update_config("max_width_pct", w.get_value()))
        grid.attach(self.width_scale, 1, 7, 1, 1)

    def build_style_tab(self, box):
        grid = Gtk.Grid(column_spacing=12, row_spacing=12)
        box.pack_start(grid, True, True, 0)

        # Font
        grid.attach(Gtk.Label(label="Font Style & Size:", xalign=0), 0, 0, 1, 1)
        self.font_btn = Gtk.FontButton()
        self.font_btn.connect("font-set", lambda w: self.update_config("font_desc", w.get_font()))
        grid.attach(self.font_btn, 1, 0, 1, 1)

        # Color
        grid.attach(Gtk.Label(label="Text Color:", xalign=0), 0, 1, 1, 1)
        self.text_color_btn = Gtk.ColorButton()
        self.text_color_btn.set_use_alpha(True)
        self.text_color_btn.connect("color-set", self.on_text_color_set)
        grid.attach(self.text_color_btn, 1, 1, 1, 1)

        # Alignment
        grid.attach(Gtk.Label(label="Text Alignment:", xalign=0), 0, 2, 1, 1)
        self.align_combo = Gtk.ComboBoxText()
        self.align_combo.append("left", "Align Left")
        self.align_combo.append("center", "Align Center")
        self.align_combo.append("right", "Align Right")
        self.align_combo.connect("changed", lambda w: self.update_config("alignment", w.get_active_id() or "center"))
        grid.attach(self.align_combo, 1, 2, 1, 1)

        # Shadow
        self.shadow_chk = Gtk.CheckButton(label="Show Subtle Text Shadow")
        self.shadow_chk.connect("toggled", lambda w: self.update_config("show_shadow", w.get_active()))
        grid.attach(self.shadow_chk, 0, 3, 2, 1)

        # Backdrop card
        self.card_chk = Gtk.CheckButton(label="Enable Backdrop Card Container")
        self.card_chk.connect("toggled", self.on_card_toggled)
        grid.attach(self.card_chk, 0, 4, 2, 1)

        # Card settings
        self.card_settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.card_settings_box.set_margin_left(20)
        grid.attach(self.card_settings_box, 0, 5, 2, 1)

        cc_box = Gtk.Box(spacing=10)
        cc_box.pack_start(Gtk.Label(label="Card Background Color:", xalign=0), False, False, 0)
        self.card_color_btn = Gtk.ColorButton()
        self.card_color_btn.set_use_alpha(True)
        self.card_color_btn.connect("color-set", self.on_card_color_set)
        cc_box.pack_start(self.card_color_btn, False, False, 0)
        self.card_settings_box.pack_start(cc_box, False, False, 0)

        cp_box = Gtk.Box(spacing=10)
        cp_box.pack_start(Gtk.Label(label="Card Inner Padding (px):", xalign=0), False, False, 0)
        self.card_padding_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 4, 80, 2)
        self.card_padding_scale.connect("value-changed", lambda w: self.update_config("card_padding", w.get_value()))
        cp_box.pack_start(self.card_padding_scale, True, True, 0)
        self.card_settings_box.pack_start(cp_box, False, False, 0)

        cr_box = Gtk.Box(spacing=10)
        cr_box.pack_start(Gtk.Label(label="Card Corner Radius (px):", xalign=0), False, False, 0)
        self.card_radius_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 40, 2)
        self.card_radius_scale.connect("value-changed", lambda w: self.update_config("card_corner_radius", w.get_value()))
        cr_box.pack_start(self.card_radius_scale, True, True, 0)
        self.card_settings_box.pack_start(cr_box, False, False, 0)

    def build_animations_tab(self, box):
        grid = Gtk.Grid(column_spacing=12, row_spacing=12)
        box.pack_start(grid, True, True, 0)

        # Style
        grid.attach(Gtk.Label(label="Transition Effect Style:", xalign=0), 0, 0, 1, 1)
        self.anim_combo = Gtk.ComboBoxText()
        self.anim_combo.append("typewriter", "Typewriter")
        self.anim_combo.append("fade", "Fade-in")
        self.anim_combo.append("instant", "Instant Display")
        self.anim_combo.connect("changed", lambda w: self.update_config("animation_style", w.get_active_id() or "typewriter"))
        grid.attach(self.anim_combo, 1, 0, 1, 1)

        # Typing Speed
        grid.attach(Gtk.Label(label="Typewriter Speed (ms/char):", xalign=0), 0, 1, 1, 1)
        self.speed_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 20, 200, 5)
        self.speed_scale.connect("value-changed", lambda w: self.update_config("typing_speed_ms", int(w.get_value())))
        grid.attach(self.speed_scale, 1, 1, 1, 1)

        # Show Duration
        grid.attach(Gtk.Label(label="Sentence Show Duration (sec):", xalign=0), 0, 2, 1, 1)
        self.duration_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 2, 30, 1)
        self.duration_scale.connect("value-changed", lambda w: self.update_config("delay_completed_sec", w.get_value()))
        grid.attach(self.duration_scale, 1, 2, 1, 1)

        # Fade Out Duration
        grid.attach(Gtk.Label(label="Fade Out Duration (sec):", xalign=0), 0, 3, 1, 1)
        self.fade_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0.2, 4.0, 0.1)
        self.fade_scale.connect("value-changed", lambda w: self.update_config("fade_out_sec", w.get_value()))
        grid.attach(self.fade_scale, 1, 3, 1, 1)

        # Bottom Controls
        box.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 10)
        btn_box = Gtk.Box(spacing=10)
        box.pack_start(btn_box, False, False, 0)

        # Next Quote
        btn_next = Gtk.Button(label="⏭ Skip Sentence")
        btn_next.connect("clicked", self.on_skip_clicked)
        btn_box.pack_start(btn_next, True, True, 0)

        # Close
        btn_close = Gtk.Button(label="Close Panel")
        btn_close.get_style_context().add_class("primary-btn")
        btn_close.connect("clicked", lambda w: self.hide())
        btn_box.pack_start(btn_close, False, False, 0)

    # --- Setting loaders & handlers ---

    def load_settings_into_ui(self):
        c = self.config_manager

        # Presets library combo sync
        active = c.get("active_quote_file")
        if "motivational.txt" in active:
            self.preset_combo.set_active_id("motivational")
        elif "zen.txt" in active:
            self.preset_combo.set_active_id("zen")
        elif "programming.txt" in active:
            self.preset_combo.set_active_id("programming")
        else:
            self.preset_combo.set_active_id("custom")
        self.file_chooser_btn.set_filename(active)
        self.file_chooser_btn.set_visible(self.preset_combo.get_active_id() == "custom")

        self.shuffle_chk.set_active(c.get("shuffle"))
        self.autostart_chk.set_active(is_autostart_enabled())
        self.monitor_combo.set_active_id(str(c.get("monitor_index")))

        preset = c.get("position_preset")
        self.pos_combo.set_active_id(preset)
        self.x_scale.set_value(c.get("custom_x_pct"))
        self.y_scale.set_value(c.get("custom_y_pct"))
        self.custom_box.set_visible(preset == "Custom")
        self.width_scale.set_value(c.get("max_width_pct"))

        # Style & backdrop
        self.font_btn.set_font(c.get("font_desc"))
        self.text_color_btn.set_rgba(self.list_to_rgba(c.get("text_color")))
        self.align_combo.set_active_id(c.get("alignment"))
        self.shadow_chk.set_active(c.get("show_shadow"))
        self.card_chk.set_active(c.get("show_card"))
        self.card_color_btn.set_rgba(self.list_to_rgba(c.get("card_color")))
        self.card_padding_scale.set_value(c.get("card_padding"))
        self.card_radius_scale.set_value(c.get("card_corner_radius"))
        self.card_settings_box.set_visible(c.get("show_card"))

        # Animations
        self.anim_combo.set_active_id(c.get("animation_style"))
        self.speed_scale.set_value(c.get("typing_speed_ms"))
        self.duration_scale.set_value(c.get("delay_completed_sec"))
        self.fade_scale.set_value(c.get("fade_out_sec"))

    def on_preset_changed(self, combo):
        preset = combo.get_active_id()
        base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "quotes")
        self.file_chooser_btn.set_visible(preset == "custom")
        if preset == "motivational":
            self.update_config("active_quote_file", os.path.join(base_dir, "motivational.txt"))
        elif preset == "zen":
            self.update_config("active_quote_file", os.path.join(base_dir, "zen.txt"))
        elif preset == "programming":
            self.update_config("active_quote_file", os.path.join(base_dir, "programming.txt"))
        elif preset == "custom":
            fn = self.file_chooser_btn.get_filename()
            if fn:
                self.update_config("active_quote_file", fn)

    def on_custom_file_set(self, widget):
        fn = widget.get_filename()
        if fn:
            self.update_config("active_quote_file", fn)

    def on_autostart_toggled(self, widget):
        if widget.get_active():
            enable_autostart(self.main_py_path)
        else:
            disable_autostart()

    def on_pos_changed(self, combo):
        val = combo.get_active_id() or "Bottom Center"
        self.update_config("position_preset", val)
        self.custom_box.set_visible(val == "Custom")

    def on_card_toggled(self, widget):
        active = widget.get_active()
        self.update_config("show_card", active)
        self.card_settings_box.set_visible(active)

    def on_text_color_set(self, widget):
        rgba = widget.get_rgba()
        self.update_config("text_color", [rgba.red, rgba.green, rgba.blue, rgba.alpha])

    def on_card_color_set(self, widget):
        rgba = widget.get_rgba()
        self.update_config("card_color", [rgba.red, rgba.green, rgba.blue, rgba.alpha])

    def on_skip_clicked(self, widget):
        if self.app and self.app.overlay:
            self.app.overlay.trigger_next_quote()

    def on_close(self, widget, event):
        self.hide()
        return True # Inhibit default window destruction

    # Helpers
    def list_to_rgba(self, lst):
        rgba = Gdk.RGBA()
        rgba.red, rgba.green, rgba.blue, rgba.alpha = lst[0], lst[1], lst[2], lst[3]
        return rgba
