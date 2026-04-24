from src.gui.styles.constants import SPACING_SM, SPACING_MD, CARD_PADX, INNER_PADX, ENTRY_HEIGHT
import customtkinter as ctk
from src.services.logging_service import log as logger
from src.gui.styles.theme import Theme
from src.gui.widgets.common import (
    page_header,
    make_card,
    card_spacer,
    field_row,
)


class TrialBalanceSchedule:
    @staticmethod
    def create_frame(parent, fv, sl):
        def g(k, v="0"):
            return fv.setdefault(k, ctk.StringVar(value=v))

        f = ctk.CTkFrame(parent, fg_color="transparent")
        page_header(
            f,
            "TRIAL BALANCE",
            "Profit & Loss summary for the financial year",
        )
        di = make_card(f, "DIRECT INCOMES", title_color=Theme.SUCCESS_GREEN)

        from src.services.io.import_service import ImportService
        ctk.CTkButton(
            di,
            text="📈 IMPORT FROM EXCEL / CSV",
            command=lambda: ImportService.import_trial_balance(fv),
            height=ENTRY_HEIGHT,
            font=Theme.BODY_BOLD,
            **Theme.get_button_style("primary")
        ).pack(fill="x", padx=INNER_PADX, pady=(SPACING_SM, 15))

        field_row(di, "Sales / Turnover", g("tb_sales"))
        field_row(di, "Direct Income", g("tb_dir_income"))
        card_spacer(di)
        de = make_card(f, "DIRECT EXPENSES", title_color=Theme.ERROR_RED)
        field_row(de, "Purchases", g("tb_purchase"))
        field_row(de, "Direct Expenses", g("tb_dir_exp"))
        field_row(de, "Salaries & Wages", g("tb_sal"))
        field_row(de, "Rent", g("tb_rent"))
        field_row(de, "Depreciation", g("tb_depr"))
        card_spacer(de)
        ii = make_card(f, "INDIRECT INCOMES", title_color=Theme.SUCCESS_GREEN)
        field_row(ii, "Interest Received", g("tb_int_rec"))
        field_row(ii, "Other Income", g("tb_oth_inc"))
        field_row(ii, "Other Indirect Incomes", g("tb_ind_income"))
        card_spacer(ii)
        ie = make_card(f, "INDIRECT EXPENSES", title_color=Theme.ERROR_RED)
        field_row(ie, "Interest Paid", g("tb_int_paid"))
        field_row(ie, "Other Indirect Expenses", g("tb_ind_exp"))
        card_spacer(ie)
        sm = make_card(f, pady_bottom=16)
        for col in range(3):
            sm.grid_columnconfigure(col, weight=1)
        sl["tb_total_dr"] = ctk.CTkLabel(
            sm,
            textvariable=g("tb_total_dr"),
            font=Theme.H2,
            text_color=Theme.ERROR_RED,
            anchor="center"
        )
        sl["tb_total_dr"].grid(row=0, column=0, sticky="e", padx=CARD_PADX, pady=SPACING_MD)
        sl["tb_total_cr"] = ctk.CTkLabel(
            sm,
            textvariable=g("tb_total_cr"),
            font=Theme.H2,
            text_color=Theme.SUCCESS_GREEN,
            anchor="center"
        )
        sl["tb_total_cr"].grid(row=0, column=1, sticky="e", padx=CARD_PADX, pady=SPACING_MD)

        def up(*_):
            try:
                d = float(g("tb_total_dr").get() or 0)
                c = float(g("tb_total_cr").get() or 0)
                ok = abs(d - c) < 1
                sl["tb_status"].configure(
                    text="BALANCED" if ok else f"DIFF: ₹ {abs(d - c):,.0f}",
                    text_color=Theme.SUCCESS_GREEN if ok else Theme.ERROR_RED,
                )
            except (ValueError, TypeError) as e:
                logger.debug(f"TB calculation failed: {e}")

        if hasattr(fv, "register_trace"):
            fv.register_trace(g("tb_total_dr"), "write", up)
            fv.register_trace(g("tb_total_cr"), "write", up)
        else:
            g("tb_total_dr").trace_add("write", up)
            g("tb_total_cr").trace_add("write", up)
        sl["tb_status"] = ctk.CTkLabel(
            sm,
            text="BALANCED",
            font=Theme.H2,
            text_color=Theme.SUCCESS_GREEN,
            anchor="center"
        )
        sl["tb_status"].grid(row=0, column=2, sticky="e", padx=CARD_PADX, pady=SPACING_MD)
        ctk.CTkLabel(
            sm,
            text="TOTAL DEBIT",
            font=Theme.CAPTION,
            text_color=Theme.TEXT_DIM,
            anchor="center"
        ).grid(row=1, column=0, sticky="w", pady=(0, SPACING_SM))
        ctk.CTkLabel(
            sm,
            text="TOTAL CREDIT",
            font=Theme.CAPTION,
            text_color=Theme.TEXT_DIM,
            anchor="center"
        ).grid(row=1, column=1, sticky="w", pady=(0, SPACING_SM))
        ctk.CTkLabel(
            sm, text="STATUS", font=Theme.CAPTION, text_color=Theme.TEXT_DIM, anchor="center"
        ).grid(row=1, column=2, sticky="w", pady=(0, SPACING_SM))
        return f
