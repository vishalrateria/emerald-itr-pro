import customtkinter as ctk
from src.gui.styles.theme import Theme
from src.gui.styles.constants import SPACING_SM
from ..widgets.section_label import section_label
from ..widgets.form_row import create_entry, create_toggle, create_combo


def build_page_ai(dialog, p):
    section_label(p, "AI Features")

    create_toggle(p, "Enable AI Features", dialog._v_ai_enabled)
    create_entry(p, "Model Path (.gguf)", dialog._v_ai_model_path, "models/...")
    create_entry(p, "Confidence Threshold (0.0-1.0)", dialog._v_ai_confidence, "0.85")
    create_entry(p, "Max Tokens", dialog._v_ai_max_tokens, "2048")
    create_entry(p, "Temperature", dialog._v_ai_temp, "0.1")
    create_entry(p, "Thread Pool Size (Async limit)", dialog._v_ai_thread_pool, "1")

    section_label(p, "Hardware Config")

    create_combo(
        p,
        "Hardware Profile",
        dialog._v_ai_hw_profile,
        ["auto", "eco", "standard", "pro"],
    )
