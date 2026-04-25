from src.config import MAX_ENTRIES_TDS, MAX_ENTRIES_TCS, MAX_ENTRIES_TAX_PAID
from src.gui.styles.constants import (
    SPACING_MD,
)
import customtkinter as ctk
from src.gui.styles.theme import Theme
from src.gui.widgets.common import (
    page_header,
    make_card,
    table_header_frame,
    table_data_row,
)


class TaxPaidSchedule:
    @staticmethod
    def create_frame(parent, fv, validation_refs=None, settings=None):
        if settings is None:
            settings = {}

        tds_limit = int(settings.get("max_entries_tds", MAX_ENTRIES_TDS))
        tcs_limit = int(settings.get("max_entries_tcs", MAX_ENTRIES_TCS))
        tax_paid_limit = int(settings.get("max_entries_tax_paid", MAX_ENTRIES_TAX_PAID))

        f = ctk.CTkFrame(parent, fg_color="transparent")
        page_header(
            f,
            "TAXES PAID",
            "TDS / TCS / Advance Tax / Self-Assessment Tax",
            accent_color=Theme.SUCCESS_GREEN,
        )

        tds_card = make_card(
            f,
            "TDS — Tax Deducted at Source",
            pady_bottom=2,
            accent_color=Theme.SUCCESS_GREEN,
        )
        table_header_frame(
            tds_card,
            [
                ("TAN", 1),
                ("Deductor Name", 2),
                ("Sec.", 1),
                ("Cert No.", 1),
                ("Date (DD-MM-YYYY)", 1),
                ("Amount ₹", 1),
            ],
        )
        for i in range(tds_limit):
            table_data_row(
                tds_card,
                i,
                [
                    {"textvariable": fv[f"tds_{i}_tan"], "key": f"tds_{i}_tan"},
                    {
                        "textvariable": fv[f"tds_{i}_name"],
                        "key": f"tds_{i}_name",
                        "weight": 2,
                    },
                    {"textvariable": fv[f"tds_{i}_section"], "key": f"tds_{i}_section"},
                    {"textvariable": fv[f"tds_{i}_cert"], "key": f"tds_{i}_cert"},
                    {"textvariable": fv[f"tds_{i}_date"], "key": f"tds_{i}_date"},
                    {"textvariable": fv[f"tds_{i}_amount"], "key": f"tds_{i}_amount"},
                ],
                validation_refs=validation_refs,
            )

        ctk.CTkFrame(f, height=SPACING_MD, fg_color="transparent").pack()
        tcs_card = make_card(
            f,
            "TCS — Tax Collected at Source",
            pady_bottom=2,
            accent_color=Theme.SUCCESS_GREEN,
        )
        table_header_frame(
            tcs_card,
            [
                ("TAN", 1),
                ("Collector Name", 2),
                ("Sec.", 1),
                ("Date (DD-MM-YYYY)", 1),
                ("Amount ₹", 1),
            ],
        )
        for i in range(tcs_limit):
            table_data_row(
                tcs_card,
                i,
                [
                    {"textvariable": fv[f"tcs_{i}_tan"], "key": f"tcs_{i}_tan"},
                    {
                        "textvariable": fv[f"tcs_{i}_name"],
                        "key": f"tcs_{i}_name",
                        "weight": 2,
                    },
                    {"textvariable": fv[f"tcs_{i}_section"], "key": f"tcs_{i}_section"},
                    {"textvariable": fv[f"tcs_{i}_date"], "key": f"tcs_{i}_date"},
                    {"textvariable": fv[f"tcs_{i}_amount"], "key": f"tcs_{i}_amount"},
                ],
                validation_refs=validation_refs,
            )

        ctk.CTkFrame(f, height=SPACING_MD, fg_color="transparent").pack()
        tax_card = make_card(
            f,
            "ADVANCE TAX / SELF-ASSESSMENT",
            pady_bottom=2,
            accent_color=Theme.SUCCESS_GREEN,
        )
        table_header_frame(
            tax_card,
            [
                ("BSR Code", 1),
                ("Challan Sr No.", 1),
                ("Date (DD-MM-YYYY)", 1),
                ("Amount ₹", 1),
                ("Type", 1),
            ],
        )
        for i in range(tax_paid_limit):
            table_data_row(
                tax_card,
                i,
                [
                    {"textvariable": fv[f"tax_{i}_bsr"], "key": f"tax_{i}_bsr"},
                    {"textvariable": fv[f"tax_{i}_challan"], "key": f"tax_{i}_challan"},
                    {"textvariable": fv[f"tax_{i}_date"], "key": f"tax_{i}_date"},
                    {"textvariable": fv[f"tax_{i}_amount"], "key": f"tax_{i}_amount"},
                    {
                        "values": ["Advance", "Self-Assessment", "TDS Regular"],
                        "variable": fv[f"tax_{i}_type"],
                    },
                ],
                validation_refs=validation_refs,
            )

        return f
