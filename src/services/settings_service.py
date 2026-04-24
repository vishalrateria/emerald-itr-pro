import json
import os
from pathlib import Path
from src.services.logging_service import log as logger

SETTINGS_FILE = Path("settings.json")

DEFAULTS: dict = {
    "autosave_interval_ms": 300000,
    "default_itr_type": "ITR-4",
    "open_last_client_on_startup": True,
    "app_title_prefix": "EMERALD ITR PRO",

    "database_path": "clients/clients.mcdb",
    "backup_folder": "backups/clients",
    "max_rolling_backups": 5,
    "auto_backup_enabled": True,

    "pdf_save_path": "",
    "ca_name": "",
    "ca_reg_number": "",
    "firm_name": "",
    "membership_number": "",

    "ui_scale_override": 0,
    "font_scale": "Normal",
    "show_shortcut_tooltips": True,

    "debounce_interval_ms": 300,
    "enable_live_recompute": True,
    "log_level": "INFO",

    "max_entries_bank": 5,
    "max_entries_tds": 10,
    "max_entries_tcs": 10,
    "max_entries_vda": 10,
    "max_business_entities": 10,
    "max_house_properties": 5,
    "max_entries_ae": 10,
    "max_entries_fo": 10,
    "max_entries_cg": 10,
    "max_entries_g": 5,
    "max_entries_hp": 5,
    "max_entries_tax_paid": 10,
    "max_cg_quarters": 5,
    "max_entries_44ad": 10,
    "itr1_gti_limit": 5000000,
}

class SettingsManager:
    _cache: dict | None = None

    @classmethod
    def _path(cls) -> Path:
        return SETTINGS_FILE

    @classmethod
    def load(cls) -> dict:
        if cls._cache is not None:
            return cls._cache
        try:
            if cls._path().exists():
                with open(cls._path(), "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    merged = {**DEFAULTS, **loaded}
                    cls._cache = merged
                    return cls._cache
        except Exception as e:
            logger.warning(f"[SettingsManager] Could not load settings: {e}")
        cls._cache = dict(DEFAULTS)
        return cls._cache

    @classmethod
    def save(cls, data: dict) -> bool:
        try:
            cls._cache = {**DEFAULTS, **data}
            to_save = dict(cls._cache)
            with open(cls._path(), "w", encoding="utf-8") as f:
                json.dump(to_save, f, indent=2, ensure_ascii=False)
            logger.info("[SettingsManager] Settings saved.")
            return True
        except Exception as e:
            logger.error(f"[SettingsManager] Could not save settings: {e}")
            return False

    @classmethod
    def get(cls, key: str, fallback=None):
        return cls.load().get(key, DEFAULTS.get(key, fallback))

    @classmethod
    def set(cls, key: str, value) -> None:
        settings = cls.load()
        settings[key] = value
        cls.save(settings)

    @classmethod
    def reset_to_defaults(cls) -> None:
        cls._cache = None
        if cls._path().exists():
            try:
                os.remove(cls._path())
            except Exception as e:
                logger.warning(f"[SettingsManager] Could not delete settings file: {e}")
        cls._cache = dict(DEFAULTS)

    @classmethod
    def get_autosave_options(cls) -> list[tuple[str, int]]:
        return [
            ("Off", 0),
            ("1 minute", 60000),
            ("3 minutes", 180000),
            ("5 minutes", 300000),
            ("10 minutes", 600000),
        ]

    @classmethod
    def get_font_scale_options(cls) -> list[str]:
        return ["Normal", "Large", "Extra Large"]

    @classmethod
    def get_itr_type_options(cls) -> list[str]:
        return ["ITR-1", "ITR-2", "ITR-3", "ITR-4"]
