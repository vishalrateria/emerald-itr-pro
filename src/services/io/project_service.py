from typing import Any
import os
import json
from datetime import datetime
from tkinter import filedialog, messagebox
from src.services.logging_service import log as logger
from src.services.io.persistence import safe_save_json, safe_load_json


class ProjectService:
    progress_callback = None

    @staticmethod
    def _validate_path(path: str) -> bool:
        return os.path.isfile(path) and os.path.getsize(path) < 10 * 1024 * 1024

    @staticmethod
    def backup_data(form_vars: dict) -> None:
        folder = filedialog.askdirectory(title="Select Backup Folder")
        if not folder:
            return
        try:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(folder, f"emerald_backup_{ts}.json")
            cache = {k: v.get() for k, v in form_vars.items() if hasattr(v, "get")}
            safe_save_json(path, cache)
            messagebox.showinfo("Backup Success", f"Backup saved to {path}")
        except Exception as e:
            logger.error(f"Backup failed: {e}")

    @staticmethod
    def restore_data(form_vars: dict) -> None:
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not path:
            return
        try:
            data = safe_load_json(path)
            if data:
                for k, v in data.items():
                    if k in form_vars:
                        form_vars[k].set(str(v))
                messagebox.showinfo("Success", "Project data restored.")
        except Exception as e:
            logger.error(f"Restore failed: {e}")

    @staticmethod
    def silent_autosave(client_master: Any) -> None:
        if client_master and client_master.current_client_id:
            try:
                client_master.save_current_client_state()
                logger.debug(f"Auto-saved state for {client_master.current_client_id}")
            except Exception as e:
                logger.error(f"Silent autosave failed: {e}")
