import customtkinter as ctk
from src.gui.styles.theme import Theme
from src.gui.styles.constants import SPACING_SM
from src.services.settings_service import SettingsManager
from ..widgets.section_label import section_label
from ..widgets.form_row import create_combo, create_toggle


def build_page_appearance(dialog, p):
    section_label(p, "Appearance")

    dialog._v_font_scale = ctk.StringVar()
    dialog._v_tooltips = ctk.BooleanVar()

    create_combo(p, "Font Scale", dialog._v_font_scale,
                SettingsManager.get_font_scale_options())
    create_toggle(p, "Show Keyboard Shortcut Tooltips", dialog._v_tooltips)

    section_label(p, "Theme")
    ctk.CTkLabel(p, text="✓ Dark Theme",
                 font=Theme.BODY_BOLD, text_color=Theme.SUCCESS_GREEN,
                 anchor="w", justify="left").pack(fill="x", pady=(0, SPACING_SM))
    ctk.CTkLabel(p, text="This application uses dark theme for optimal visibility and reduced eye strain.",
                 font=Theme.CAPTION, text_color=Theme.TEXT_MUTED,
                 anchor="w", justify="left").pack(fill="x", pady=(0, SPACING_SM))
