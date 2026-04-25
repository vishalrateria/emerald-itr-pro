import customtkinter as ctk
from src.services.settings_service import SettingsManager
from ..widgets.section_label import section_label
from ..widgets.form_row import create_toggle


def build_page_notifications(dialog, p):
    section_label(p, "Notifications & Alerts")

    create_toggle(p, "ITR Due Date Reminders", dialog._v_due_date_remind)
    create_toggle(p, "Backup Completion Notifications", dialog._v_backup_notify)
    create_toggle(p, "Error & Critical Alerts", dialog._v_error_alerts)
    create_toggle(p, "App Update Available Notifications", dialog._v_update_notify)
    create_toggle(p, "Show Autosave HUD / Notifications", dialog._v_autosave_notify)
