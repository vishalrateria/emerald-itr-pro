import customtkinter as ctk
from ..widgets.section_label import section_label
from ..widgets.form_row import create_entry, create_toggle, create_combo


def build_page_advanced(dialog, p):
    section_label(p, "Performance & System")

    dialog._v_debounce = ctk.StringVar()
    dialog._v_live_recompute = ctk.BooleanVar()
    dialog._v_log_level = ctk.StringVar()

    create_entry(p, "Calculation Debounce (ms)", dialog._v_debounce, "300")
    create_toggle(p, "Enable Live Re-computation", dialog._v_live_recompute)
    create_combo(p, "Logging Level", dialog._v_log_level, ["DEBUG", "INFO", "WARNING", "ERROR"])
