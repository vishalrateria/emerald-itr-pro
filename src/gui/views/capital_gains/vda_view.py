from src.gui.styles.constants import SPACING_MD
import customtkinter as ctk
from src.gui.styles.theme import Theme
from src.gui.widgets.common import (
    page_header,
    make_card,
    info_banner,
    table_header_frame,
    table_data_row,
)


class VDASchedule:
    @staticmethod
    def create_frame(parent, fv, validation_refs=None, settings=None):
        if settings is None:
            settings = {}
        vda_limit = int(settings.get("max_entries_vda", 10))
        f = ctk.CTkFrame(parent, fg_color="transparent")
        page_header(
            f,
            "SCHEDULE VDA — VIRTUAL DIGITAL ASSETS",
            "Crypto & NFT (VDA) | Taxable @ 30% flat | " "No deduction / set-off",
        )
        info_banner(
            f,
            "⚠  30% FLAT TAX",
            "VDA gains are taxed @ flat 30% with no deduction for "
            "expenses (except cost of acquisition). Losses cannot "
            "be set off against any other income.",
            color=Theme.WARNING,
        )
        make_card(f, "VDA TRANSACTIONS", pady_bottom=2)
        table_header_frame(
            f,
            [
                ("Token / Coin", 1),
                ("Type", 1),
                ("Exchange", 1),
                ("Cost ₹", 1),
                ("Sale ₹", 1),
                ("Acq Date", 1),
                ("Tx Date", 1),
            ],
        )
        for i in range(vda_limit):
            table_data_row(
                f,
                i,
                [
                    {"textvariable": fv[f"vda_{i}_token"], "key": f"vda_{i}_token"},
                    {"textvariable": fv[f"vda_{i}_type"], "key": f"vda_{i}_type"},
                    {
                        "textvariable": fv[f"vda_{i}_exchange"],
                        "key": f"vda_{i}_exchange",
                    },
                    {"textvariable": fv[f"vda_{i}_cost"], "key": f"vda_{i}_cost"},
                    {"textvariable": fv[f"vda_{i}_sale"], "key": f"vda_{i}_sale"},
                    {
                        "textvariable": fv[f"vda_{i}_acq_date"],
                        "key": f"vda_{i}_acq_date",
                    },
                    {
                        "textvariable": fv[f"vda_{i}_trans_date"],
                        "key": f"vda_{i}_trans_date",
                    },
                ],
                validation_refs=validation_refs,
            )
        ctk.CTkFrame(f, height=SPACING_MD, fg_color="transparent").pack()
        return f
