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


class STCGSchedule:
    @staticmethod
    def create_frame(parent, fv, sl, validation_refs=None):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        page_header(
            f,
            "SCHEDULE 111A — SHORT-TERM CAPITAL GAINS",
            "STCG on listed equity / equity MF  |  Taxable @ 20%",
        )
        make_card(f, "TRANSACTION-WISE STCG", pady_bottom=2)
        table_header_frame(
            f,
            [
                ("Asset / Scrip Name", 2),
                ("Cost of Acquisition ₹", 1),
                ("Sale Consideration ₹", 1),
                ("STCG ₹", 1),
            ],
        )
        for i in range(10):
            table_data_row(
                f,
                i,
                [
                    {
                        "textvariable": fv[f"stcg_{i}_asset"],
                        "key": f"stcg_{i}_asset",
                        "font": Theme.BODY,
                        **Theme.get_entry_style(),
                        "weight": 2,
                    },
                    {
                        "textvariable": fv[f"stcg_{i}_cost"],
                        "key": f"stcg_{i}_cost",
                        "font": Theme.DATA,
                        "justify": "right",
                        **Theme.get_entry_style(),
                        "weight": 1,
                    },
                    {
                        "textvariable": fv[f"stcg_{i}_sale"],
                        "key": f"stcg_{i}_sale",
                        "font": Theme.DATA,
                        "justify": "right",
                        **Theme.get_entry_style(),
                        "weight": 1,
                    },
                    {
                        "textvariable": fv[f"stcg_{i}_stcg"],
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
        tot_card = make_card(f, pady_bottom=10)
        total_row(
            tot_card,
            "TOTAL STCG  (u/s 111A)",
            "stcg_sum",
            sl,
            color=Theme.SUCCESS_GREEN,
        )
        info_banner(
            f,
            "ℹ  TAX RATE",
            "STCG u/s 111A is taxable @ 20% from AY 2026-27 "
            "(Budget 2024 amendment). "
            "Applies to transfers on or after 23-Jul-2024.",
            color=Theme.ACCENT_PRIMARY,
        )
        return f
