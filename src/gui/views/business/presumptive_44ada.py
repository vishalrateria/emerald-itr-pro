from src.gui.styles.constants import SPACING_SM, SPACING_MD, SPACING_LG
import customtkinter as ctk
from src.gui.styles.theme import Theme
from src.gui.widgets.common import (
    page_header,
    make_card,
    total_row,
    info_banner,
    table_header_frame,
    table_data_row,
    combo_field_row,
)


class Presumptive44ADASchedule:
    @staticmethod
    def create_frame(parent, fv, sl, validation_refs=None):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        page_header(
            f,
            "SCHEDULE 44ADA — PRESUMPTIVE PROFESSION INCOME",
            "Presumptive income @ 50% for specified professionals",
        )
        info_banner(
            f,
            "ℹ  RECEIPTS LIMIT",
            "Section 44ADA applies to professionals with receipts up to "
            "₹75 Lakh (AY 2026-27). Income is presumed @ 50%.",
            color=Theme.ACCENT_PRIMARY,
        )
        lim_card = make_card(f, "LIMIT APPLICABILITY")
        combo_field_row(
            lim_card,
            "Cash Receipts as % of Total Receipts",
            fv["cash_txn_slab"],
            ["<= 5%", "> 5%"],
        )
        ctk.CTkLabel(
            lim_card,
            text="If cash receipts are <= 5%, limit is ₹75 Lakh. If > 5%, limit is ₹50 Lakh.",
            text_color=Theme.TEXT_DIM,
            font=Theme.CAPTION,
            anchor="w",
        ).pack(fill="x", padx=SPACING_LG, pady=(0, SPACING_SM))
        make_card(f, "PROFESSION-WISE DETAILS", pady_bottom=2)
        table_header_frame(
            f,
            [
                ("Profession / Client Name", 3),
                ("Gross Receipts ₹", 2),
                ("Presumptive Income ₹  (50%)", 2),
            ],
        )
        for i in range(10):
            table_data_row(
                f,
                i,
                [
                    {
                        "textvariable": fv[f"ada_{i}_name"],
                        "key": f"ada_{i}_name",
                        "font": Theme.BODY,
                        **Theme.get_entry_style(),
                        "weight": 3,
                    },
                    {
                        "textvariable": fv[f"ada_{i}_gross"],
                        "key": f"ada_{i}_gross",
                        "font": Theme.DATA,
                        "justify": "right",
                        **Theme.get_entry_style(),
                        "weight": 2,
                    },
                    {
                        "textvariable": fv[f"ada_{i}_inc_44ada"],
                        "font": Theme.DATA,
                        "justify": "right",
                        "state": "readonly",
                        **Theme.get_entry_style("calc"),
                        "weight": 2,
                    },
                ],
                validation_refs=validation_refs,
            )
        ctk.CTkFrame(f, height=SPACING_MD, fg_color="transparent").pack()
        tot_card = make_card(f, pady_bottom=16)
        total_row(
            tot_card,
            "TOTAL 44ADA INCOME",
            "ada_total",
            sl,
            color=Theme.SUCCESS_GREEN,
        )
        return f
