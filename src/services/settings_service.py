import json
import os
from pathlib import Path
from src.services.logging_service import log as logger

SETTINGS_FILE = Path("settings.json")


def _merge_dicts(default_d, loaded_d):
    merged = dict(default_d)
    if not isinstance(loaded_d, dict):
        return merged
    for k, v in loaded_d.items():
        if isinstance(v, dict) and k in merged and isinstance(merged[k], dict):
            merged[k] = _merge_dicts(merged[k], v)
        else:
            merged[k] = v
    return merged


DEFAULTS: dict = {
    "General": {
        "app_title_prefix": "EMERALD ITR PRO",
        "default_itr_type": "ITR-1",
        "open_last_client_on_startup": True,
        "recent_clients": [],
        "ca_firm": {
            "ca_name": "",
            "ca_reg_number": "",
            "firm_name": "",
            "membership_number": "",
        },
    },
    "Data": {
        "database_path": "clients/clients.mcdb",
        "backup_folder": "backups/clients",
        "max_rolling_backups": 10,
        "auto_backup_enabled": True,
        "autosave_interval_ms": 300000,
    },
    "Appearance": {
        "ui_scale_override": 0,
        "font_scale": "Normal",
        "show_shortcut_tooltips": True,
        "window_geometry": "1536x801+64+64",
        "window_maximized": True,
    },
    "Engine": {
        "debounce_interval_ms": 300,
        "enable_live_recompute": True,
        "log_level": "INFO",
        "pdf_save_path": "",
        "show_debug_overlay": False,
    },
    "ITR_Limits": {
        "Common": {
            "max_entries_bank": 5,
            "max_entries_tax_paid": 10,
            "max_entries_tcs": 10,
            "max_entries_tds": 20,
            "max_entries_g": 10,
        },
        "ITR1": {"gti_limit": 5000000},
        "ITR2": {
            "max_entries_cg": 20,
            "max_cg_quarters": 5,
            "max_house_properties": 5,
            "max_entries_hp": 10,
            "max_entries_vda": 10,
            "max_entries_fo": 20,
        },
        "ITR3": {"max_business_entities": 15, "max_entries_ae": 15},
        "ITR4": {"max_entries_44ad": 15, "max_entries_44ada": 15},
    },
    "AI": {
        "enabled": True,
        "model_path": "models/Phi-4-mini-instruct-Q8_0.gguf",
        "confidence_threshold": 0.90,
        "max_tokens": 4096,
        "temperature": 0.1,
        "thread_pool_size": 1,
        "hardware_profile": "auto",
        "n_ctx": 4096,
        "n_gpu_layers": 0,
        "n_threads": 4,
    },
    "Export": {
        "default_format": "PDF",
        "pdf_quality": "High",
        "include_schedules": True,
        "auto_open_after_gen": True,
        "json_indent": 2,
    },
    "Backup": {"schedule": "Daily", "compression": "lzma", "retention_days": 60},
    "Notifications": {
        "due_date_reminder": True,
        "backup_completion": True,
        "error_alerts": True,
        "update_available": True,
        "autosave_notification": True,
    },
    "Window": {
        "start_minimized": False,
        "minimize_to_tray_on_close": False,
        "always_on_top": False,
        "show_on_startup": True,
    },
    "Computation": {
        "default_regime": "New (115BAC)",
        "round_off_totals": True,
        "show_detailed_calc": True,
        "show_marginal_relief": True,
        "allow_negative_values": False,
        "interest_method": "Simple",
    },
    "ITR_Behavior": {
        "autosave_form_progress": True,
        "validate_on_exit": True,
        "show_inline_errors": True,
        "allow_partial_submission": False,
        "default_schedule_selections": "S, HP, CG, OS",
    },
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

                    if "autosave_interval_ms" in loaded:
                        logger.info(
                            "Legacy flat settings detected. Migrating to nested schema."
                        )
                        cls._cache = dict(DEFAULTS)
                        cls.save(cls._cache)
                        return cls._cache

                    merged = _merge_dicts(DEFAULTS, loaded)
                    cls._cache = merged
                    return cls._cache
        except Exception as e:
            logger.warning(f"[SettingsManager] Could not load settings: {e}")
        cls._cache = dict(DEFAULTS)
        return cls._cache

    @classmethod
    def save(cls, data: dict) -> bool:
        try:
            cls._cache = _merge_dicts(DEFAULTS, data)
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
        env_key = key.replace(".", "_").upper()
        if env_key in os.environ:
            val_str = os.environ[env_key]
            if val_str.lower() in ("true", "false"):
                return val_str.lower() == "true"
            try:
                return int(val_str)
            except ValueError:
                try:
                    return float(val_str)
                except ValueError:
                    return val_str

        keys = key.split(".")
        val = cls.load()
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return fallback
        return val

    @classmethod
    def set(cls, key: str, value) -> None:
        settings = cls.load()
        keys = key.split(".")
        d = settings
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value
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
            ("2 minutes", 120000),
            ("3 minutes", 180000),
            ("4 minutes", 240000),
            ("5 minutes", 300000),
            ("6 minutes", 360000),
            ("8 minutes", 480000),
            ("10 minutes", 600000),
        ]

    @classmethod
    def get_font_scale_options(cls) -> list[str]:
        return ["Normal", "Large", "Extra Large"]

    @classmethod
    def get_itr_type_options(cls) -> list[str]:
        return ["ITR-1", "ITR-2", "ITR-3", "ITR-4"]

    @classmethod
    def get_export_format_options(cls) -> list[str]:
        return ["PDF", "JSON", "Excel"]

    @classmethod
    def get_pdf_quality_options(cls) -> list[str]:
        return ["Standard", "High", "Compressed"]

    @classmethod
    def get_backup_schedule_options(cls) -> list[str]:
        return ["Manual", "Daily", "Weekly"]

    @classmethod
    def get_compression_options(cls) -> list[str]:
        return ["zip", "gzip", "lzma"]

    @classmethod
    def get_regime_options(cls) -> list[str]:
        return ["New (115BAC)"]

    @classmethod
    def get_interest_method_options(cls) -> list[str]:
        return ["Simple", "Compound"]
