from src.gui.styles.constants import SPACING_SM, SPACING_MD, INNER_PADX
import customtkinter as ctk
from src.services.logging_service import log as logger
from src.gui.styles.theme import Theme
from src.gui.widgets.common import (
    page_header,
    make_card,
    card_spacer,
    field_row,
)


class BalanceSheetSchedule:
    @staticmethod
    def create_frame(parent, fv, sl):
        def g(k, v="0"):
            return fv.setdefault(k, ctk.StringVar(value=v))

        f = ctk.CTkFrame(parent, fg_color="transparent")
        page_header(
            f,
            "BALANCE SHEET",
            "Statement of Assets & Liabilities as at 31st March",
        )
        lib = make_card(f, "LIABILITIES", title_color=Theme.ERROR_RED)
        field_row(lib, "Capital Account", g("bs_cap"))
        field_row(lib, "Reserves & Surplus", g("bs_res"))
        field_row(lib, "Loans Taken  (Secured + Unsecured)", g("bs_loans"))
        field_row(lib, "Sundry Creditors", g("bs_creditors"))
        field_row(lib, "Bank Overdraft", g("bs_od"))
        field_row(lib, "Provision for Tax", g("bs_prov_tax"))
        card_spacer(lib)
        ast = make_card(f, "ASSETS", title_color=Theme.SUCCESS_GREEN)
        field_row(ast, "Land & Building", g("bs_land"))
        field_row(ast, "Plant & Machinery", g("bs_plant"))
        field_row(ast, "Furniture & Fixtures", g("bs_furn"))
        field_row(ast, "Sundry Debtors", g("bs_debtors"))
        field_row(ast, "Inventory / Closing Stock", g("bs_inv"))
        field_row(ast, "Cash in Hand", g("bs_cash"))
        field_row(ast, "Bank Balance", g("bs_bank"))
        field_row(ast, "Loans & Advances Given", g("bs_loan_given"))
        field_row(ast, "Investments", g("bs_invmt"))
        card_spacer(ast)
        sm = make_card(f, pady_bottom=16)
        for col in range(4):
            sm.grid_columnconfigure(col, weight=1)

        sl["bs_equity_total"] = ctk.CTkLabel(
            sm,
            text="₹ 0",
            font=Theme.H2,
            text_color=Theme.TEXT_PRIMARY,
            anchor="center",
        )
        sl["bs_equity_total"].grid(
            row=0, column=0, sticky="e", padx=INNER_PADX, pady=SPACING_MD
        )

        sl["bs_liab_total_val"] = ctk.CTkLabel(
            sm, text="₹ 0", font=Theme.H2, text_color=Theme.ERROR_RED, anchor="center"
        )
        sl["bs_liab_total_val"].grid(
            row=0, column=1, sticky="e", padx=INNER_PADX, pady=SPACING_MD
        )

        sl["bs_assets_total_val"] = ctk.CTkLabel(
            sm,
            text="₹ 0",
            font=Theme.H2,
            text_color=Theme.SUCCESS_GREEN,
            anchor="center",
        )
        sl["bs_assets_total_val"].grid(
            row=0, column=2, sticky="e", padx=INNER_PADX, pady=SPACING_MD
        )

        sl["bs_status"] = ctk.CTkLabel(
            sm,
            text="BALANCED",
            font=Theme.H2,
            text_color=Theme.SUCCESS_GREEN,
            anchor="center",
        )
        sl["bs_status"].grid(
            row=0, column=3, sticky="e", padx=INNER_PADX, pady=SPACING_MD
        )

        def up(*_):
            try:
                cap = float(g("bs_cap").get() or 0)
                res = float(g("bs_res").get() or 0)
                liab = sum(
                    float(g(k).get() or 0)
                    for k in ["bs_loans", "bs_creditors", "bs_od", "bs_prov_tax"]
                )
                assets = sum(
                    float(g(k).get() or 0)
                    for k in [
                        "bs_land",
                        "bs_plant",
                        "bs_furn",
                        "bs_debtors",
                        "bs_inv",
                        "bs_cash",
                        "bs_bank",
                        "bs_loan_given",
                        "bs_invmt",
                    ]
                )

                equity = cap + res
                total_l = equity + liab
                diff = assets - total_l
                ok = abs(diff) < 1

                sl["bs_equity_total"].configure(text=f"₹ {int(equity):,}")
                sl["bs_liab_total_val"].configure(text=f"₹ {int(liab):,}")
                sl["bs_assets_total_val"].configure(text=f"₹ {int(assets):,}")
                sl["bs_status"].configure(
                    text="BALANCED" if ok else f"DIFF: ₹ {int(abs(diff)):,}",
                    text_color=Theme.SUCCESS_GREEN if ok else Theme.ERROR_RED,
                )
            except (ValueError, TypeError) as e:
                logger.debug(f"Balance sheet computation failed: {e}")

        for k in [
            "bs_cap",
            "bs_res",
            "bs_loans",
            "bs_creditors",
            "bs_od",
            "bs_prov_tax",
            "bs_land",
            "bs_plant",
            "bs_furn",
            "bs_debtors",
            "bs_inv",
            "bs_cash",
            "bs_bank",
            "bs_loan_given",
            "bs_invmt",
        ]:
            if hasattr(fv, "register_trace"):
                fv.register_trace(g(k), "write", up)
            else:
                g(k).trace_add("write", up)

        ctk.CTkLabel(
            sm,
            text="TOTAL EQUITY",
            font=Theme.CAPTION,
            text_color=Theme.TEXT_DIM,
            anchor="center",
        ).grid(row=1, column=0, sticky="w", pady=(0, SPACING_SM))
        ctk.CTkLabel(
            sm,
            text="LIABILITIES",
            font=Theme.CAPTION,
            text_color=Theme.TEXT_DIM,
            anchor="center",
        ).grid(row=1, column=1, sticky="w", pady=(0, SPACING_SM))
        ctk.CTkLabel(
            sm,
            text="TOTAL ASSETS",
            font=Theme.CAPTION,
            text_color=Theme.TEXT_DIM,
            anchor="center",
        ).grid(row=1, column=2, sticky="w", pady=(0, SPACING_SM))
        ctk.CTkLabel(
            sm,
            text="STATUS",
            font=Theme.CAPTION,
            text_color=Theme.TEXT_DIM,
            anchor="center",
        ).grid(row=1, column=3, sticky="w", pady=(0, SPACING_SM))
        return f
