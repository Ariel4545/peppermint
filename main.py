#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from peppermint.config import ConfigManager
from peppermint.quotes import QuotesManager
from peppermint.daemon import PeppermintApp

def main():
    show_gui_on_startup = True
    if "--daemon" in sys.argv:
        show_gui_on_startup = False
        sys.argv.remove("--daemon")
        print("Starting in background daemon mode...")

    if "--settings" in sys.argv:
        show_gui_on_startup = True
        sys.argv.remove("--settings")
        print("Starting in Settings mode...")

    gtk_args = [sys.argv[0]]

    config_manager = ConfigManager()
    quotes_manager = QuotesManager(
        active_file_path=config_manager.get("active_quote_file"),
        shuffle=config_manager.get("shuffle")
    )

    main_py_path = os.path.abspath(__file__)

    app = PeppermintApp(
        config_manager=config_manager,
        quotes_manager=quotes_manager,
        main_py_path=main_py_path,
        show_gui_on_activate=show_gui_on_startup
    )

    try:
        sys.exit(app.run(gtk_args))
    except KeyboardInterrupt:
        print("\nExiting Peppermint...")
        app.quit()

if __name__ == "__main__":
    main()
