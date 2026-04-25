from src.config import MAX_ENTRIES_HP
from src.gui.styles.constants import (
    SPACING_MD,
)
import customtkinter as ctk
from src.gui.styles.theme import Theme
from src.gui.widgets.common import (
    page_header,
    make_card,
    info_banner,
    table_header_frame,
    table_data_row,
)


class HousePropertySchedule:
    @staticmethod
    def create_frame(
        parent: ctk.CTkFrame, fv: dict, validation_refs: dict = None
    ) -> ctk.CTkFrame:
        f = ctk.CTkFrame(parent, fg_color="transparent")
        page_header(
            f,
            "SCHEDULE HP  —  HOUSE PROPERTY",
            "Income from house property  |  New Tax Regime",
        )
        info_banner(
            f,
            "⚠  NEW REGIME RESTRICTION",
            "Interest on Self-Occupied property is NOT deductible. "
            "Set-off of house property loss is restricted under the "
            "new regime.",
            color=Theme.ERROR_RED,
        )
        make_card(f, "PROPERTY-WISE INCOME", pady_bottom=2)
        table_header_frame(
            f,
            [
                ("Prop", 1),
                ("Type", 2),
                ("Annual Rent ₹", 2),
                ("Unrealised ₹", 2),
                ("Muni Tax ₹", 1),
                ("Interest ₹", 1),
                ("Net ₹", 2),
            ],
        )
        for i in range(MAX_ENTRIES_HP):
            nk = f"hp_{i}_net"
            table_data_row(
                f,
                i,
                [
                    {
                        "text": f"P{i + 1}",
                        "font": Theme.BODY_BOLD,
                        "text_color": Theme.TEXT_DIM,
                        "weight": 1,
                    },
                    {
                        "values": ["let-out", "self-occupied"],
                        "variable": fv[f"hp_{i}_type"],
                        "font": Theme.BODY,
                        **Theme.get_combo_style(),
                        "weight": 2,
                    },
                    {
                        "textvariable": fv[f"hp_{i}_rent"],
                        "key": f"hp_{i}_rent",
                        "font": Theme.DATA,
                        "justify": "right",
                        **Theme.get_entry_style(),
                        "weight": 2,
                    },
                    {
                        "textvariable": fv[f"hp_{i}_unrealised_rent"],
                        "key": f"hp_{i}_unrealised_rent",
                        "font": Theme.DATA,
                        "justify": "right",
                        **Theme.get_entry_style(),
                        "weight": 2,
                    },
                    {
                        "textvariable": fv[f"hp_{i}_muni_tax"],
                        "key": f"hp_{i}_muni_tax",
                        "font": Theme.DATA,
                        "justify": "right",
                        **Theme.get_entry_style(),
                        "weight": 1,
                    },
                    {
                        "textvariable": fv[f"hp_{i}_int_loan"],
                        "key": f"hp_{i}_int_loan",
                        "font": Theme.DATA,
                        "justify": "right",
                        **Theme.get_entry_style(),
                        "weight": 1,
                        "tooltip": "Interest paid on home loan during the financial year.",
                    },
                    {
                        "textvariable": fv[nk],
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
        make_card(f, "TENANT & ADDRESS DETAILS", pady_bottom=2)
        table_header_frame(
            f,
            [
                ("Prop", 1),
                ("Tenant PAN", 2),
                ("Property Address", 4),
                ("Co-Owner PAN", 2),
            ],
        )
        for i in range(MAX_ENTRIES_HP):
            table_data_row(
                f,
                i,
                [
                    {
                        "text": f"P{i + 1}",
                        "font": Theme.BODY_BOLD,
                        "text_color": Theme.TEXT_DIM,
                        "weight": 1,
                    },
                    {
                        "textvariable": fv[f"hp_{i}_tenant"],
                        "key": f"hp_{i}_tenant",
                        "font": Theme.DATA,
                        **Theme.get_entry_style(),
                        "weight": 2,
                    },
                    {
                        "textvariable": fv[f"hp_{i}_address"],
                        "key": f"hp_{i}_address",
                        "font": Theme.BODY,
                        **Theme.get_entry_style(),
                        "weight": 4,
                    },
                    {
                        "textvariable": fv[f"hp_{i}_co_owner"],
                        "key": f"hp_{i}_co_owner",
                        "font": Theme.DATA,
                        **Theme.get_entry_style(),
                        "weight": 2,
                    },
                ],
                validation_refs=validation_refs,
            )
        return f
