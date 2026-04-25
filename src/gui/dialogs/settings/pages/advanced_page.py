import customtkinter as ctk
from ..widgets.section_label import section_label
from ..widgets.form_row import create_entry, create_toggle, create_combo


def build_page_advanced(dialog, p):
    section_label(p, "Performance & System")

    create_entry(p, "Calculation Debounce (ms)", dialog._v_debounce, "300")
    create_toggle(p, "Enable Live Re-computation", dialog._v_live_recompute)
    create_combo(
        p, "Logging Level", dialog._v_log_level, ["DEBUG", "INFO", "WARNING", "ERROR"]
    )

    section_label(p, "Maintenance")

    from src.gui.styles.theme import Theme
    from src.gui.styles.constants import BUTTON_HEIGHT, ACTION_BUTTON_WIDTH_LG

    btn_grid = ctk.CTkFrame(p, fg_color="transparent")
    btn_grid.pack(fill="x", pady=10)

    ctk.CTkButton(
        btn_grid,
        text="📄  Export Diagnostic Logs",
        width=ACTION_BUTTON_WIDTH_LG,
        height=BUTTON_HEIGHT,
        font=Theme.BODY_BOLD,
        command=dialog._handle_export_logs,
        **Theme.get_button_style("secondary")
    ).grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")

    ctk.CTkButton(
        btn_grid,
        text="🧠  Reset AI Model Cache",
        width=ACTION_BUTTON_WIDTH_LG,
        height=BUTTON_HEIGHT,
        font=Theme.BODY_BOLD,
        command=dialog._handle_reset_ai_cache,
        **Theme.get_button_style("secondary")
    ).grid(row=0, column=1, padx=(0, 10), pady=5, sticky="w")

    ctk.CTkButton(
        btn_grid,
        text="🧹  Clear Temporary Files",
        width=ACTION_BUTTON_WIDTH_LG,
        height=BUTTON_HEIGHT,
        font=Theme.BODY_BOLD,
        command=dialog._handle_clear_temp,
        **Theme.get_button_style("secondary")
    ).grid(row=1, column=0, padx=(0, 10), pady=5, sticky="w")
