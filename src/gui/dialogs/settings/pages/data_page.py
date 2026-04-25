import customtkinter as ctk
from ..widgets.section_label import section_label
from ..widgets.form_row import create_combo, create_toggle
from ..widgets.path_row import create_path_row


def build_page_data(dialog, p):
    section_label(p, "Database")

    create_path_row(p, "Database File (.mcdb)", dialog._v_db_path, mode="file")
    create_path_row(p, "Backup Folder", dialog._v_backup_folder, mode="dir")

    section_label(p, "Backup Policy")
    create_combo(
        p, "Max Rolling Backups", dialog._v_max_backups, ["3", "5", "10", "20", "50"]
    )
    create_toggle(p, "Auto-Backup on Save", dialog._v_auto_backup)

    from src.services.settings_service import SettingsManager
    from src.gui.styles.theme import Theme
    from src.gui.styles.constants import BUTTON_HEIGHT, ACTION_BUTTON_WIDTH_LG

    create_combo(
        p,
        "Backup Schedule",
        dialog._v_backup_schedule,
        SettingsManager.get_backup_schedule_options(),
    )
    create_combo(
        p,
        "Backup Compression",
        dialog._v_backup_compression,
        SettingsManager.get_compression_options(),
    )
    create_combo(
        p,
        "Retention Days",
        dialog._v_backup_retention,
        ["7", "15", "30", "60", "90", "365"],
    )

    section_label(p, "Cloud Integration")
    ctk.CTkButton(
        p,
        text="☁️  Connect to Google Drive / OneDrive",
        width=ACTION_BUTTON_WIDTH_LG,
        height=BUTTON_HEIGHT,
        font=Theme.BODY_BOLD,
        state="disabled",
        command=lambda: None,
        **Theme.get_button_style("secondary")
    ).pack(anchor="w", pady=(5, 10))
    ctk.CTkLabel(
        p,
        text="Cloud backup features coming in v2.0",
        font=Theme.CAPTION,
        text_color=Theme.TEXT_MUTED,
    ).pack(anchor="w")

    section_label(p, "Data Management")

    btn_frame = ctk.CTkFrame(p, fg_color="transparent")
    btn_frame.pack(fill="x", pady=10)

    ctk.CTkButton(
        btn_frame,
        text="📦  Manual Backup Now",
        width=ACTION_BUTTON_WIDTH_LG,
        height=BUTTON_HEIGHT,
        font=Theme.BODY_BOLD,
        command=dialog._handle_manual_backup,
        **Theme.get_button_style("secondary")
    ).pack(side="left", padx=(0, 10))

    ctk.CTkButton(
        btn_frame,
        text="🗑️  Clear Cache",
        width=ACTION_BUTTON_WIDTH_LG,
        height=BUTTON_HEIGHT,
        font=Theme.BODY_BOLD,
        command=dialog._handle_clear_cache,
        **Theme.get_button_style("danger")
    ).pack(side="left")
