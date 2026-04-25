from src.gui.styles.constants import SPACING_XS, SPACING_SM, INNER_PADX
import customtkinter as ctk
from src.services.logging_service import log as logger
from src.gui.styles.theme import Theme
from src.gui.widgets.common import page_header, make_card


class AuditSchedule:
    @staticmethod
    def create_frame(parent, fv, sl):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        page_header(
            f,
            "AUDIT WORKSPACE",
            "Side-by-side comparison: Return vs. External Data (AIS/26AS)",
        )

        comp_card = make_card(f, "DATA RECONCILIATION")

        headers = ["Source Category", "Amount in Return", "Amount in AIS", "Status"]
        h_row = ctk.CTkFrame(comp_card, fg_color=Theme.BG_PRIMARY)
        h_row.pack(fill="x", padx=INNER_PADX, pady=SPACING_SM)
        h_row.grid_columnconfigure((0, 1, 2, 3), weight=1)
        for i, h in enumerate(headers):
            ctk.CTkLabel(
                h_row,
                text=h,
                font=Theme.BODY_BOLD,
                text_color=Theme.TEXT_PRIMARY,
                anchor="w" if i == 0 else "e",
            ).grid(row=0, column=i, sticky="ew", padx=INNER_PADX, pady=SPACING_SM)

        def _comp_row(label, return_key, ais_val, row_idx):
            row = ctk.CTkFrame(comp_card, fg_color="transparent")
            row.pack(fill="x", padx=INNER_PADX, pady=SPACING_SM)
            row.grid_columnconfigure((0, 1, 2, 3), weight=1)

            ctk.CTkLabel(
                row, text=label, font=Theme.BODY, text_color=Theme.TEXT_DIM, anchor="w"
            ).grid(row=0, column=0, sticky="ew", padx=INNER_PADX)

            ret_lbl = ctk.CTkLabel(row, text="₹ 0", font=Theme.BODY_BOLD, anchor="e")
            ret_lbl.grid(row=0, column=1, sticky="ew", padx=INNER_PADX)
            sl[f"audit_ret_{return_key}"] = ret_lbl

            ctk.CTkLabel(
                row,
                text=f"₹ {int(ais_val):,}",
                font=Theme.BODY,
                text_color=Theme.ACCENT_PRIMARY,
                anchor="e",
            ).grid(row=0, column=2, sticky="ew", padx=INNER_PADX)

            stat_lbl = ctk.CTkLabel(
                row,
                text="PENDING",
                font=Theme.CAPTION,
                text_color=Theme.TEXT_DIM,
                anchor="e",
            )
            stat_lbl.grid(row=0, column=3, sticky="ew", padx=INNER_PADX)
            sl[f"audit_stat_{return_key}"] = stat_lbl

            setattr(stat_lbl, "_ais_val", ais_val)

        ais_sal, ais_int, ais_div, ais_tds, ais_bp = 0, 0, 0, 0, 0
        try:
            from src.services.io.import_service import ImportService

            ais_data = getattr(ImportService, "ais_cache", {})
            if ais_data:
                for entry in ais_data.get("tds_details", []):
                    ais_tds += int(entry.get("amount", 0))
                ais_sal = int(ais_data.get("salary_total", 0))
                ais_int = int(ais_data.get("interest_total", 0))
                ais_div = int(ais_data.get("dividend_total", 0))
                ais_bp = int(ais_data.get("business_receipts_total", 0))
        except Exception as e:
            logger.error(f"Failed to load AIS data: {e}")

        _comp_row("Salary Income", "sal_gross", ais_sal, 0)
        _comp_row("Business / Professional Receipts", "bp_total", ais_bp, 1)
        _comp_row("Interest Income", "os_interest", ais_int, 2)
        _comp_row("Dividend Income", "os_dividend", ais_div, 3)
        _comp_row("TDS / Tax Credits", "it_total", ais_tds, 4)

        return f
