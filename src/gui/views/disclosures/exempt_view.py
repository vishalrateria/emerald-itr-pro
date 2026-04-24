import customtkinter as ctk
from src.gui.widgets.common import (
    page_header,
    make_card,
    card_spacer,
    field_row,
)


class ExemptIncomeSchedule:
    @staticmethod
    def create_frame(parent, fv):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        page_header(
            f,
            "SCHEDULE EI — EXEMPT INCOME",
            "Income exempt from tax — reported but not included in GTI",
        )
        ei_card = make_card(f, "EXEMPT INCOME SOURCES")
        field_row(
            ei_card,
            "Agricultural Income (exempt — not part of GTI)",
            fv["ei_agri"],
        )
        field_row(ei_card, "PPF Interest / LIC Maturity / Other Exempt", fv["ei_other"])
        card_spacer(ei_card)
        return f
