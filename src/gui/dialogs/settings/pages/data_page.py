import customtkinter as ctk
from ..widgets.section_label import section_label
from ..widgets.form_row import create_combo, create_toggle
from ..widgets.path_row import create_path_row


def build_page_data(dialog, p):
    section_label(p, "Database")

    dialog._v_db_path = ctk.StringVar()
    dialog._v_backup_folder = ctk.StringVar()
    dialog._v_max_backups = ctk.StringVar()
    dialog._v_auto_backup = ctk.BooleanVar()

    create_path_row(p, "Database File (.mcdb)", dialog._v_db_path, mode="file")
    create_path_row(p, "Backup Folder", dialog._v_backup_folder, mode="dir")

    section_label(p, "Backup Policy")
    create_combo(p, "Max Rolling Backups", dialog._v_max_backups,
                ["3", "5", "10", "20", "50"])
    create_toggle(p, "Auto-Backup on Save", dialog._v_auto_backup)
