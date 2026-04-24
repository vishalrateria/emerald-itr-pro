import customtkinter as ctk
import json
import os
from src.services.settings_service import SettingsManager
from ..widgets.section_label import section_label
from ..widgets.form_row import create_combo, create_toggle, create_entry


def build_page_general(dialog, p):
    section_label(p, "General")

    dialog._v_autosave = ctk.StringVar()
    dialog._v_default_itr = ctk.StringVar()
    dialog._v_open_last = ctk.BooleanVar()
    dialog._v_title_prefix = ctk.StringVar()
    dialog._v_ai_enabled = ctk.BooleanVar()

    autosave_labels = [o[0] for o in SettingsManager.get_autosave_options()]
    create_combo(p, "Autosave Interval", dialog._v_autosave, autosave_labels)
    create_combo(p, "Default ITR Type", dialog._v_default_itr,
                SettingsManager.get_itr_type_options())
    create_toggle(p, "Open Last Client on Startup", dialog._v_open_last)
    create_entry(p, "Window Title Prefix", dialog._v_title_prefix,
                "e.g. EMERALD ITR PRO")

    section_label(p, "AI Assistant")
    create_toggle(p, "Enable AI Data Extraction", dialog._v_ai_enabled)

    ai_profile_label = ctk.CTkLabel(
        p,
        text="",
        font=ctk.CTkFont(size=12),
        text_color="#888888"
    )
    ai_profile_label.pack(anchor="w", padx=150, pady=(0, 10))
    dialog._ai_profile_label = ai_profile_label

    _update_ai_profile_display(ai_profile_label)


def _update_ai_profile_display(label):
    try:
        from src.services.ai.hardware_utils import get_hardware_profile
        profile = get_hardware_profile()
        profile_labels = {
            "eco": "Eco (< 8GB RAM) - AI Disabled",
            "standard": "Standard (8-12GB RAM) - Limited Mode",
            "pro": "Pro (> 12GB RAM) - Full Mode"
        }
        label.configure(text=f"Hardware Profile: {profile_labels.get(profile, profile)}")
    except Exception:
        label.configure(text="Hardware Profile: Unknown")


def load_ai_settings():
    """Load AI settings from settings.json"""
    settings_path = "settings.json"
    try:
        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                settings = json.load(f)
            return settings.get("ai_enabled", True)
    except Exception:
        pass
    return True


def save_ai_settings(enabled: bool):
    """Save AI settings to settings.json"""
    settings_path = "settings.json"
    try:
        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                settings = json.load(f)
        else:
            settings = {}

        settings["ai_enabled"] = enabled

        with open(settings_path, "w") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        from src.services.logging_service import log as logger
        logger.error(f"Failed to save AI settings: {e}")
