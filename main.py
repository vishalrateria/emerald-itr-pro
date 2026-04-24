import sys
import os
import customtkinter as ctk
from src.services.logging_service import setup_logger

def _create_required_folders():
    """Create required directories on first run."""
    folders = ['data', 'models', 'clients', 'backups', 'exports']
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

_create_required_folders()
setup_logger()

from src.gui.application import EmeraldITRMain

if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                windll.user32.SetProcessDPIAware()
            except Exception:
                pass

    app = EmeraldITRMain()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
