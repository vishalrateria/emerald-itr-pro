import customtkinter as ctk
from src.services.settings_service import SettingsManager
from ..widgets.section_label import section_label
from ..widgets.form_row import create_combo, create_toggle


def build_page_computation(dialog, p):
    section_label(p, "Tax Computation")

    from ..widgets.form_row import create_row
    from src.gui.styles.theme import Theme

    row = create_row(p, "Default Tax Regime")
    ctk.CTkLabel(
        row, text="New (115BAC)", font=Theme.BODY_BOLD, text_color=Theme.ACCENT_PRIMARY
    ).grid(row=0, column=1, sticky="w")
    create_toggle(p, "Round Off Totals to Nearest Rupee", dialog._v_round_off)
    create_toggle(p, "Show Detailed Step-by-Step Calculations", dialog._v_show_calc)
    create_toggle(p, "Visualize Marginal Relief (New Regime)", dialog._v_show_relief)
    create_toggle(p, "Allow Negative Values in Forms", dialog._v_allow_negative)
    create_combo(
        p,
        "Interest Calculation Method",
        dialog._v_interest_method,
        SettingsManager.get_interest_method_options(),
    )
