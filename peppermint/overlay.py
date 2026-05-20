import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Gtk, Gdk, GLib, Pango, PangoCairo
import cairo
import math

class WallpaperOverlay(Gtk.Window):
    def __init__(self, config_manager, quotes_manager):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.config_manager = config_manager
        self.quotes_manager = quotes_manager

        self.set_decorated(False)
        self.set_app_paintable(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_keep_below(True)
        self.stick()

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)

        self.connect("realize", self.on_realize)
        self.connect("draw", self.on_draw)
        self.update_geometry()

        self.anim_state = "waiting"
        self.current_quote = ""
        self.is_paused = False
        self.typed_chars = 0
        self.alpha_factor = 1.0

        self.timer_id = None
        self.state_timer_id = None

        GLib.timeout_add(500, self.trigger_next_quote)

    def set_paused(self, paused):
        self.is_paused = paused
        if paused:
            self.clear_all_timers()
        else:
            self.trigger_next_quote()

    def on_realize(self, widget):
        window = self.get_window()
        if window:
            region = cairo.Region()
            window.input_shape_combine_region(region, 0, 0)

    def update_geometry(self):
        display = Gdk.Display.get_default()
        if not display:
            return
        num_monitors = display.get_n_monitors()
        monitor_idx = self.config_manager.get("monitor_index")
        monitor = display.get_primary_monitor()
        if 0 <= monitor_idx < num_monitors:
            monitor = display.get_monitor(monitor_idx)
        if monitor:
            geom = monitor.get_geometry()
            self.set_default_size(geom.width, geom.height)
            self.move(geom.x, geom.y)
            self.queue_draw()

    def clear_all_timers(self):
        if self.timer_id:
            GLib.source_remove(self.timer_id)
            self.timer_id = None
        if self.state_timer_id:
            GLib.source_remove(self.state_timer_id)
            self.state_timer_id = None

    def trigger_next_quote(self):
        if self.is_paused:
            return False
        self.clear_all_timers()
        self.current_quote = self.quotes_manager.get_next()
        self.typed_chars = 0
        self.alpha_factor = 1.0

        style = self.config_manager.get("animation_style")
        if style == "typewriter" and self.current_quote:
            self.anim_state = "typing"
            speed = max(10, self.config_manager.get("typing_speed_ms"))
            self.timer_id = GLib.timeout_add(speed, self.tick_typewriter)
        elif style == "fade" and self.current_quote:
            self.anim_state = "typing"
            self.alpha_factor = 0.0
            self.timer_id = GLib.timeout_add(30, self.tick_fade_in)
        else:
            self.anim_state = "completed"
            self.typed_chars = len(self.current_quote)
            self.queue_draw()
            delay = int(self.config_manager.get("delay_completed_sec") * 1000)
            self.state_timer_id = GLib.timeout_add(delay, self.trigger_fade_out)
        return False

    def tick_typewriter(self):
        if self.anim_state != "typing":
            return False
        if self.typed_chars < len(self.current_quote):
            self.typed_chars += 1
            self.queue_draw()
            return True
        else:
            self.anim_state = "completed"
            delay = int(self.config_manager.get("delay_completed_sec") * 1000)
            self.state_timer_id = GLib.timeout_add(delay, self.trigger_fade_out)
            return False

    def tick_fade_in(self):
        if self.anim_state != "typing":
            return False
        self.alpha_factor += 0.05
        if self.alpha_factor >= 1.0:
            self.alpha_factor = 1.0
            self.anim_state = "completed"
            self.typed_chars = len(self.current_quote)
            self.queue_draw()
            delay = int(self.config_manager.get("delay_completed_sec") * 1000)
            self.state_timer_id = GLib.timeout_add(delay, self.trigger_fade_out)
            return False
        self.typed_chars = len(self.current_quote)
        self.queue_draw()
        return True

    def trigger_fade_out(self):
        self.clear_all_timers()
        self.anim_state = "fading"
        self.timer_id = GLib.timeout_add(30, self.tick_fade_out)
        return False

    def tick_fade_out(self):
        if self.anim_state != "fading":
            return False
        fade_out_sec = max(0.1, self.config_manager.get("fade_out_sec"))
        self.alpha_factor -= 0.03 / fade_out_sec
        if self.alpha_factor <= 0.0:
            self.alpha_factor = 0.0
            self.anim_state = "waiting"
            self.queue_draw()
            delay = int(self.config_manager.get("delay_next_sec") * 1000)
            self.state_timer_id = GLib.timeout_add(delay, self.trigger_next_quote)
            return False
        self.queue_draw()
        return True

    def draw_rounded_rectangle(self, cr, x, y, w, h, radius):
        cr.new_sub_path()
        cr.arc(x + w - radius, y + radius, radius, -math.pi/2, 0)
        cr.arc(x + w - radius, y + h - radius, radius, 0, math.pi/2)
        cr.arc(x + radius, y + h - radius, radius, math.pi/2, math.pi)
        cr.arc(x + radius, y + radius, radius, math.pi, 3*math.pi/2)
        cr.close_path()

    def on_draw(self, widget, cr):
        cr.set_source_rgba(0, 0, 0, 0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()

        if not self.current_quote or self.alpha_factor <= 0.0:
            return False

        cr.set_operator(cairo.OPERATOR_OVER)
        c = self.config_manager

        font_desc_str = c.get("font_desc")
        text_color = c.get("text_color").copy()
        alignment_str = c.get("alignment")
        show_shadow = c.get("show_shadow")
        shadow_color = c.get("shadow_color").copy()
        shadow_ox = c.get("shadow_offset_x")
        shadow_oy = c.get("shadow_offset_y")

        show_card = c.get("show_card")
        card_color = c.get("card_color").copy()
        card_border_color = c.get("card_border_color").copy()
        card_border_width = c.get("card_border_width")
        card_radius = c.get("card_corner_radius")
        card_padding = c.get("card_padding")
        max_width_pct = c.get("max_width_pct")

        preset = c.get("position_preset")
        cx_pct = c.get("custom_x_pct")
        cy_pct = c.get("custom_y_pct")

        text_color[3] *= self.alpha_factor
        shadow_color[3] *= self.alpha_factor
        card_color[3] *= self.alpha_factor
        card_border_color[3] *= self.alpha_factor

        display_text = self.current_quote[:self.typed_chars]
        if self.anim_state == "typing" and c.get("animation_style") == "typewriter":
            display_text += "|"

        layout = self.create_pango_layout(display_text)
        layout.set_font_description(Pango.FontDescription(font_desc_str))
        align = Pango.Alignment.CENTER
        if alignment_str == "left":
            align = Pango.Alignment.LEFT
        elif alignment_str == "right":
            align = Pango.Alignment.RIGHT
        layout.set_alignment(align)

        window_width = self.get_allocated_width()
        window_height = self.get_allocated_height()
        max_width_px = window_width * (max_width_pct / 100.0)
        layout.set_width(int(max_width_px * Pango.SCALE))
        layout.set_wrap(Pango.WrapMode.WORD_CHAR)

        text_w, text_h = layout.get_pixel_size()
        box_w = text_w + (card_padding * 2 if show_card else 0)
        box_h = text_h + (card_padding * 2 if show_card else 0)

        margin = 50.0
        if preset == "Top Left":
            x, y = margin, margin
        elif preset == "Top Center":
            x, y = (window_width - box_w) / 2.0, margin
        elif preset == "Top Right":
            x, y = window_width - box_w - margin, margin
        elif preset == "Middle Left":
            x, y = margin, (window_height - box_h) / 2.0
        elif preset == "Center":
            x, y = (window_width - box_w) / 2.0, (window_height - box_h) / 2.0
        elif preset == "Middle Right":
            x, y = window_width - box_w - margin, (window_height - box_h) / 2.0
        elif preset == "Bottom Left":
            x, y = margin, window_height - box_h - margin
        elif preset == "Bottom Center":
            x, y = (window_width - box_w) / 2.0, window_height - box_h - margin
        elif preset == "Bottom Right":
            x, y = window_width - box_w - margin, window_height - box_h - margin
        else: # Custom
            x = (window_width - box_w) * (cx_pct / 100.0)
            y = (window_height - box_h) * (cy_pct / 100.0)

        x = max(0, min(window_width - box_w, x))
        y = max(0, min(window_height - box_h, y))

        if show_card:
            cr.set_source_rgba(*card_color)
            self.draw_rounded_rectangle(cr, x, y, box_w, box_h, card_radius)
            cr.fill()
            if card_border_width > 0:
                cr.set_source_rgba(*card_border_color)
                cr.set_line_width(card_border_width)
                self.draw_rounded_rectangle(cr, x, y, box_w, box_h, card_radius)
                cr.stroke()

        tx = x + (card_padding if show_card else 0)
        ty = y + (card_padding if show_card else 0)

        if show_shadow:
            cr.set_source_rgba(*shadow_color)
            cr.move_to(tx + shadow_ox, ty + shadow_oy)
            PangoCairo.show_layout(cr, layout)

        cr.set_source_rgba(*text_color)
        cr.move_to(tx, ty)
        PangoCairo.show_layout(cr, layout)
        return False
