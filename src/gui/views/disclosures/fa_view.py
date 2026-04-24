import customtkinter as ctk
from src.gui.styles.theme import Theme
from src.gui.widgets.common import (
    page_header,
    make_card,
    field_row,
    combo_field_row,
    info_banner,
)


class ForeignAssetsSchedule:
    @staticmethod
    def create_frame(parent, fv):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        page_header(
            f,
            "SCHEDULE FA — FOREIGN ASSETS",
            "Disclosure of foreign assets and income from any source outside India",
        )

        info_banner(
            f,
            "ℹ  MANDATORY DISCLOSURE",
            "ROR taxpayers must disclose all foreign assets held between 1 Apr 2025 and 31 Mar 2026. "
            "Failure to disclose may attract severe penalties under Black Money Act.",
            color=Theme.ERROR_RED,
        )

        fa_card = make_card(f, "FOREIGN ASSET DETAILS")
        combo_field_row(
            fa_card,
            "Asset Category",
            fv["fa_category"],
            [
                "Depository Account",
                "Custodial Account",
                "Equity/Debt Interest",
                "Immovable Property",
                "Others",
            ],
        )
        field_row(fa_card, "Entity Name & Address", fv["fa_entity"])
        field_row(fa_card, "Country Name / Code", fv["fa_country"])
        field_row(fa_card, "Initial Value ₹", fv["fa_initial_val"])
        field_row(fa_card, "Peak Balance during Year ₹", fv["fa_peak_val"])

        return f
