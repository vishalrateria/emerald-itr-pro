from src.gui.styles.constants import SPACING_MD
import customtkinter as ctk
from src.gui.styles.theme import Theme
from src.gui.widgets.common import (
    page_header,
    make_card,
    total_row,
    info_banner,
    table_header_frame,
    table_data_row,
)


class Presumptive44ADSchedule:
    @staticmethod
    def create_frame(parent, fv, sl, validation_refs=None):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        page_header(
            f,
            "SCHEDULE 44AD — PRESUMPTIVE BUSINESS INCOME",
            "Presumptive income @ 8% of turnover (6% for digital receipts)",
        )
        from src.config import PRESUMPTIVE_44AD_LIMIT_BASE, PRESUMPTIVE_44AD_LIMIT_ENHANCED
        info_banner(
            f,
            "ℹ  TURNOVER LIMIT",
            f"Section 44AD applies to businesses with total turnover up to "
            f"₹{int(PRESUMPTIVE_44AD_LIMIT_BASE/10000000)} Crore. Enhanced limit of ₹{int(PRESUMPTIVE_44AD_LIMIT_ENHANCED/10000000)} Crore applies if cash receipts "
            "do not exceed 5% of turnover.",
            color=Theme.ACCENT_PRIMARY,
        )
        from src.gui.widgets.common import combo_field_row, card_spacer
        limit_card = make_card(f, "LIMIT ASSESSMENT")
        combo_field_row(
            limit_card,
            "Cash receipts / payments <= 5% of total turnover?",
            fv["cash_txn_slab"],
            ["<= 5%", "> 5%"],
        )
        card_spacer(limit_card)
        make_card(f, "BUSINESS-WISE DETAILS", pady_bottom=2)
        table_header_frame(
            f,
            [
                ("Business Name", 2),
                ("Nature of Business", 2),
                ("Total Turnover ₹", 1),
                ("Digital ₹", 1),
                ("Income ₹", 1),
            ],
        )
        for i in range(10):
            table_data_row(
                f,
                i,
                [
                    {
                        "textvariable": fv[f"ad_{i}_name"],
                        "key": f"ad_{i}_name",
                        "font": Theme.BODY,
                        **Theme.get_entry_style(),
                        "weight": 2,
                    },
                    {
                        "textvariable": fv[f"ad_{i}_nature"],
                        "key": f"ad_{i}_nature",
                        "font": Theme.BODY,
                        **Theme.get_entry_style(),
                        "weight": 2,
                    },
                    {
                        "textvariable": fv[f"ad_{i}_turnover"],
                        "key": f"ad_{i}_turnover",
                        "font": Theme.DATA,
                        "justify": "right",
                        **Theme.get_entry_style(),
                        "weight": 1,
                    },
                    {
                        "textvariable": fv[f"ad_{i}_digital"],
                        "key": f"ad_{i}_digital",
                        "font": Theme.DATA,
                        "justify": "right",
                        **Theme.get_entry_style(),
                        "weight": 1,
                    },
                    {
                        "textvariable": fv[f"ad_{i}_inc_44ad"],
                        "font": Theme.DATA,
                        "justify": "right",
                        "state": "readonly",
                        **Theme.get_entry_style("calc"),
                        "weight": 1,
                    },
                ],
                validation_refs=validation_refs,
            )
        ctk.CTkFrame(f, height=SPACING_MD, fg_color="transparent").pack()
        tot_card = make_card(f, pady_bottom=16)
        total_row(
            tot_card,
            "TOTAL 44AD INCOME",
            "ad_total",
            sl,
            color=Theme.SUCCESS_GREEN,
        )
        return f
