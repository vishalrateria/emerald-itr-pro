import customtkinter as ctk
from src.gui.styles.theme import Theme
from src.gui.styles.constants import SPACING_SM
from src.services.settings_service import SettingsManager
from ..widgets.section_label import section_label
from ..widgets.form_row import create_combo, create_toggle, create_entry


def build_page_appearance(dialog, p):
    section_label(p, "Appearance")

    create_combo(
        p, "Font Scale", dialog._v_font_scale, SettingsManager.get_font_scale_options()
    )
    create_toggle(p, "Show Keyboard Shortcut Tooltips", dialog._v_tooltips)
    create_entry(p, "UI Scale Override (0 for Auto)", dialog._v_ui_scale_override, "0")
