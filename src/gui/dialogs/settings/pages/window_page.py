import customtkinter as ctk
from src.gui.styles.theme import Theme
from src.services.settings_service import SettingsManager
from ..widgets.section_label import section_label
from ..widgets.form_row import create_toggle
from src.gui.styles.constants import BUTTON_HEIGHT, ACTION_BUTTON_WIDTH_LG


def build_page_window(dialog, p):
    section_label(p, "Window Behavior")

    create_toggle(p, "Start Minimized to System Tray", dialog._v_start_minimized)
    create_toggle(p, "Minimize to Tray on Close", dialog._v_minimize_on_close)
    create_toggle(p, "Keep Application Always on Top", dialog._v_always_on_top)
    create_toggle(p, "Show Main Window on Startup", dialog._v_show_on_startup)

    ctk.CTkButton(
        p,
        text="↺  Restore Last Window Position",
        width=ACTION_BUTTON_WIDTH_LG,
        height=BUTTON_HEIGHT,
        font=Theme.BODY_BOLD,
        command=dialog._handle_restore_position,
        **Theme.get_button_style("secondary")
    ).pack(anchor="w", pady=(20, 0))
