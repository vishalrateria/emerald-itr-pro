from src.gui.styles.constants import SPACING_SM
import customtkinter as ctk
from src.gui.styles.theme import Theme
from src.gui.widgets.common import (
    page_header,
    make_card,
    card_spacer,
    field_row,
    table_header_frame,
    table_data_row,
    info_banner,
)


class VerifySchedule:
    @staticmethod
    def create_frame(parent, fv):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        page_header(
            f,
            "BANK DETAILS & VERIFICATION",
            "Refund bank account — must match ITR portal records",
        )
        pb = make_card(f, "PRIMARY BANK ACCOUNT  (Refund Credit)")
        field_row(pb, "IFSC Code", fv["bank_ifsc"])
        field_row(pb, "Account Number", fv["bank_acc"])
        card_spacer(pb)
        make_card(f, "ADDITIONAL BANK ACCOUNTS", pady_bottom=2)
        table_header_frame(
            f,
            [
                ("IFSC Code", 1),
                ("Account Number", 2),
                ("Bank Name", 2),
            ],
        )
        for i in range(5):
            table_data_row(
                f,
                i,
                [
                    {
                        "textvariable": fv[f"bank_{i}_ifsc"],
                        "font": Theme.DATA,
                        **Theme.get_entry_style(),
                        "weight": 1,
                    },
                    {
                        "textvariable": fv[f"bank_{i}_acc"],
                        "font": Theme.DATA,
                        **Theme.get_entry_style(),
                        "weight": 2,
                    },
                    {
                        "textvariable": fv[f"bank_{i}_name"],
                        "font": Theme.BODY,
                        **Theme.get_entry_style(),
                        "weight": 2,
                    },
                ],
            )
        ctk.CTkFrame(f, height=SPACING_SM, fg_color="transparent").pack()
        pl = make_card(f, "PLACE OF SIGNING")
        field_row(pl, "City / Town", fv["verification_place"])
        card_spacer(pl)

        al_card = make_card(
            f, "SCHEDULE AL — ASSETS & LIABILITIES (MANDATORY if Income > ₹50 Lakh)")
        info_banner(
            f,
            "📋 STATUTORY DISCLOSURE",
            "Required only if Total Income exceeds ₹50 Lakh. Enter cost of assets as of 31st March 2026.",
            color=Theme.ACCENT_PRIMARY
        )
        field_row(al_card, "Immovable Assets (Land/Building) ₹", fv["al_immovable"])
        field_row(al_card, "Movable Assets (Shares/Cash/Gold) ₹", fv["al_movable"])
        field_row(al_card, "Liabilities in relation to Assets ₹", fv["al_liabilities"])
        card_spacer(al_card)

        return f
