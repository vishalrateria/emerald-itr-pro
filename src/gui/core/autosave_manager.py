from datetime import datetime
from src.config import AUTOSAVE_DEBOUNCE_INTERVAL
from src.services.io.project_service import ProjectService
from src.services.logging_service import log as logger


class AutosaveMixin:
    def perform_autosave(self):
        if self.needs_save and self.client_master:
            try:
                ProjectService.silent_autosave(self.client_master)
                self.needs_save = False
                ts = datetime.now().strftime("%H:%M:%S")
                self.save_status_label.configure(text=f"Saved at {ts}")
            except Exception as e:
                logger.error(f"Autosave error: {e}")
        from src.services.settings_service import SettingsManager

        _as_ms = SettingsManager.get("Data.autosave_interval_ms", 300000)
        if _as_ms > 0:
            self._autosave_job = self.after(_as_ms, self.perform_autosave)

    def trigger_autosave_debounce(self):
        if hasattr(self, "_autosave_timer") and self._autosave_timer:
            self.after_cancel(self._autosave_timer)
        self._autosave_timer = self.after(
            AUTOSAVE_DEBOUNCE_INTERVAL, self.perform_autosave
        )
