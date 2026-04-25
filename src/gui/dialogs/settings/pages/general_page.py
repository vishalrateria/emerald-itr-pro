import customtkinter as ctk
from src.services.settings_service import SettingsManager
from ..widgets.section_label import section_label
from ..widgets.form_row import create_combo, create_toggle, create_entry


def build_page_general(dialog, p):
    section_label(p, "General")

    autosave_labels = [o[0] for o in SettingsManager.get_autosave_options()]
    create_combo(p, "Autosave Interval", dialog._v_autosave, autosave_labels)
    create_combo(
        p,
        "Default ITR Type",
        dialog._v_default_itr,
        SettingsManager.get_itr_type_options(),
    )
    create_toggle(p, "Open Last Client on Startup", dialog._v_open_last)
    create_entry(
        p, "Window Title Prefix", dialog._v_title_prefix, "e.g. EMERALD ITR PRO"
    )

    section_label(p, "ITR-Specific Behavior")

    create_toggle(p, "Auto-save Form Progress Regularly", dialog._v_autosave_form)
    create_toggle(p, "Validate Fields on Field Exit", dialog._v_validate_on_exit)
    create_toggle(p, "Show Field-level Errors Inline", dialog._v_inline_errors)

    create_entry(
        p, "Default Schedule Selections", dialog._v_def_schedules, "e.g. S, HP, CG, OS"
    )

    section_label(p, "Data Management")

    from src.gui.styles.theme import Theme
    from src.gui.styles.constants import BUTTON_HEIGHT, ACTION_BUTTON_WIDTH_LG

    btn_frame = ctk.CTkFrame(p, fg_color="transparent")
    btn_frame.pack(fill="x", pady=10)

    ctk.CTkButton(
        btn_frame,
        text="🧹  Clear Recent Clients",
        width=ACTION_BUTTON_WIDTH_LG,
        height=BUTTON_HEIGHT,
        font=Theme.BODY_BOLD,
        command=dialog._handle_clear_recent_clients,
        **Theme.get_button_style("secondary")
    ).pack(side="left", padx=(0, 10))

    ctk.CTkButton(
        btn_frame,
        text="📤  Export Settings",
        width=ACTION_BUTTON_WIDTH_LG,
        height=BUTTON_HEIGHT,
        font=Theme.BODY_BOLD,
        command=dialog._handle_export_settings,
        **Theme.get_button_style("secondary")
    ).pack(side="left", padx=(0, 10))

    ctk.CTkButton(
        btn_frame,
        text="📥  Import Settings",
        width=ACTION_BUTTON_WIDTH_LG,
        height=BUTTON_HEIGHT,
        font=Theme.BODY_BOLD,
        command=dialog._handle_import_settings,
        **Theme.get_button_style("secondary")
    ).pack(side="left")
