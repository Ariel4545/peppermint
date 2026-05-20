import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GLib
import sys

class PeppermintApp(Gtk.Application):
    def __init__(self, config_manager, quotes_manager, main_py_path, show_gui_on_activate=True):
        super().__init__(
            application_id="org.peppermint",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.config_manager = config_manager
        self.quotes_manager = quotes_manager
        self.main_py_path = main_py_path
        self.show_gui_on_activate = show_gui_on_activate
        self.first_activation = True

        self.overlay = None
        self.dashboard = None
        self.tray_icon = None
        self.is_paused = False

    def do_startup(self):
        Gtk.Application.do_startup(self)
        from peppermint.overlay import WallpaperOverlay
        self.overlay = WallpaperOverlay(self.config_manager, self.quotes_manager)
        self.overlay.show_all()

        if self.config_manager.get("run_in_tray"):
            self.setup_tray_icon()

    def do_activate(self):
        if self.first_activation:
            self.first_activation = False
            if not self.show_gui_on_activate:
                return

        if not self.dashboard:
            from peppermint.gui import SettingsDashboard
            self.dashboard = SettingsDashboard(self.config_manager, self.quotes_manager, self.main_py_path, self)
            self.add_window(self.dashboard)
        self.dashboard.show_all()
        self.dashboard.present()

    def setup_tray_icon(self):
        try:
            self.tray_icon = Gtk.StatusIcon()
            self.tray_icon.set_from_icon_name("preferences-desktop-wallpaper")
            self.tray_icon.set_tooltip_text("Peppermint")
            self.tray_icon.connect("activate", lambda icon: self.do_activate())
            self.tray_icon.connect("popup-menu", self.on_tray_popup_menu)
            self.tray_icon.set_visible(True)
        except Exception as e:
            print(f"StatusIcon not supported: {e}")

    def on_tray_popup_menu(self, icon, button, activate_time):
        menu = Gtk.Menu()

        item_settings = Gtk.MenuItem(label="⚙ Settings Panel")
        item_settings.connect("activate", lambda w: self.do_activate())
        menu.append(item_settings)

        menu.append(Gtk.SeparatorMenuItem())

        item_skip = Gtk.MenuItem(label="⏭ Skip Sentence")
        item_skip.connect("activate", lambda w: self.overlay.trigger_next_quote() if self.overlay else None)
        menu.append(item_skip)

        label_pause = "▶ Resume Typing" if self.is_paused else "⏸ Pause Typing"
        item_pause = Gtk.MenuItem(label=label_pause)
        item_pause.connect("activate", self.on_tray_toggle_pause)
        menu.append(item_pause)

        menu.append(Gtk.SeparatorMenuItem())

        item_quit = Gtk.MenuItem(label="Quit Application")
        item_quit.connect("activate", lambda w: self.quit())
        menu.append(item_quit)

        menu.show_all()
        menu.popup(None, None, Gtk.StatusIcon.position_menu, icon, button, activate_time)

    def on_tray_toggle_pause(self, widget):
        self.is_paused = not self.is_paused
        if self.overlay:
            self.overlay.set_paused(self.is_paused)

    def do_shutdown(self):
        if self.overlay:
            self.overlay.destroy()
        if self.dashboard:
            self.dashboard.destroy()
        Gtk.Application.do_shutdown(self)
