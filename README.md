# Peppermint 🎨🕊

**Peppermint** is a professional, high-performance, and extremely configurable wallpaper quote visualization program tailored specifically for Linux Mint (Cinnamon desktop environment). 

Instead of writing text to static image files on disk and spamming `gsettings` background updates (which causes desktop lag, flickering, and high CPU usage), Peppermint runs a lightweight desktop service that overlays a **transparent, borderless, fully click-through X11 window** directly on the root desktop layer. Mouse clicks pass entirely through the window, keeping your desktop folders, files, and right-click menus 100% interactive.

It beautifully prints motivational quotes, zen proverbs, or custom programming proverbs character-by-character (typewriter style) or with smooth cross-fades, turning your desktop background into a source of inspiration.

---

## Key Features ✨

1. **High-Performance Transparent Overlay:**
   - Vector graphics rendered at 60 FPS directly on the screen using **GTK3** and **Cairo/Pango**.
   - **Click-Through Capabilities:** Standard X11 input shape masking allows you to interact with all desktop elements naturally.
   - Sticky across all workspaces, hiding cleanly from the taskbar, pagers, and window switchers.
2. **Beautiful Writing Transitions & Animations:**
   - **Typewriter Effect:** Types quotes letter-by-letter with a customizable speed and a blinking cursor (`|`).
   - **Fade-in Effect:** Fades sentences smoothly on and off the screen.
   - **Instant Display:** Displays completed quotes instantly without animations.
3. **High-End Settings Dashboard:**
   - **Typography Settings:** Pick any installed system font, adjust color, sizing, alignment, and toggle anti-aliased drop shadows (offset, color, blur).
   - **Glassmorphism Containers:** Add modern glass-like background cards behind the text, with customizable background color, opacity, corner radius, inner padding, border color, and border thickness.
   - **Layout Customization:** Position text anywhere on the screen using 9 different preset anchors (Center, Bottom Center, Top Right, etc.) or absolute X/Y percentages.
4. **Built-in Quote Database Editor:**
   - Edit, delete, and add custom motivational quotes right inside the Settings Dashboard.
   - Hot-reloads in real-time when files are modified or saved.
5. **System Tray Integration:**
   - Right-click tray menu allows you to quick-skip quotes, go back in history, pause/resume typing timers, open the dashboard, or quit cleanly.
6. **Autostart & Background System Sync:**
   - Easily toggle "Autostart on Login" with a single click.
   - Apply standard wallpaper images directly from the dashboard to Cinnamon.

---

## Directory Structure 📂

```
peppermint/
├── peppermint/                # Premium Application Package (dashboard, tray, auto-locks)
│   ├── __init__.py
│   ├── config.py              # Persistent config (~/.config/peppermint/config.json)
│   ├── daemon.py              # Single-instance launcher & tray controller
│   ├── gui.py                 # Settings Dashboard
│   ├── overlay.py             # Cairo transparent desktop window overlay
│   ├── quotes.py              # Quote text files parser and queue manager
│   └── utils.py               # Autostart helpers and Cinnamon background sync
├── quotes/                    # Preloaded quotes database
│   ├── motivational.txt       # Motivational / Self-growth quotes
│   ├── programming.txt        # Programming sayings and advice
│   └── zen.txt                # Peaceful Zen proverbs
├── main.py                    # Main executable entry point
├── .gitignore                 # Files and folders to ignore in Git
└── README.md                  # This file
```

---

## How to Run 🚀

Since Linux Mint natively includes Python3 and GTK3, there are no heavy external dependencies.

### 🌟 Running the App (with Dashboard GUI & Tray Icon)
To launch the utility and open the dashboard:
```bash
./main.py
```

To run in the background (perfect for startup scripts/autostart):
```bash
./main.py --daemon
```

#### Autostart on Boot ⏰
Simply open the dashboard, navigate to the **General & Position** tab, and check **Autostart on Desktop Login**. The application will automatically create a standard desktop launcher in `~/.config/autostart/`.

---

## Customizing Quotes 📝

Each line in your selected text file represents a single sentence/quote.
- Lines starting with `#` are treated as comments and ignored.
- Empty lines are automatically skipped.

You can edit your selected quote file inside the quotes directory or choose a custom file from the settings panel!


