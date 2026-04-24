from src.gui.styles.constants import SPACING_MD, CARD_PADX
import customtkinter as ctk
from src.services.logging_service import log as logger
from src.gui.styles.theme import Theme
from src.gui.widgets.common import (
    page_header,
    make_card,
    card_spacer,
    field_row,
    table_header_frame,
    table_data_row,
)


class BusinessFinancialsSchedule:
    @staticmethod
    def create_frame(parent, fv):
        def g(k, v="0"):
            return fv.setdefault(k, ctk.StringVar(value=v))

        f = ctk.CTkFrame(parent, fg_color="transparent")
        page_header(
            f,
            "SCHEDULE BP — BUSINESS FINANCIALS",
            "Comparative financial statements & GST reconciliation | ITR-3",
        )
        nat = make_card(f, "NATURE OF BUSINESS")
        field_row(nat, "Business / Profession Description", g("bp_nature", ""))
        card_spacer(nat)
        make_card(
            f,
            "LIABILITIES  (Comparative)",
            title_color=Theme.ERROR_RED,
            pady_bottom=2,
        )
        table_header_frame(
            f,
            [
                ("Account", 2),
                ("Opening ₹", 1),
                ("Closing ₹", 1),
                ("Variance ₹", 1),
            ],
        )
        liab_items = [
            ("Capital Account", "bp_liab_cap_open", "bp_liab_cap_close"),
            (
                "Secured Loans",
                "bp_liab_loans_sec_open",
                "bp_liab_loans_sec_close",
            ),
            (
                "Unsecured Loans",
                "bp_liab_loans_unsec_open",
                "bp_liab_loans_unsec_close",
            ),
            (
                "Sundry Creditors",
                "bp_liab_creditors_open",
                "bp_liab_creditors_close",
            ),
            (
                "Loans from Partners",
                "bp_liab_partner_loans_open",
                "bp_liab_partner_loans_close",
            ),
        ]
        for idx, (lbl, o_key, c_key) in enumerate(liab_items):
            v_key = o_key.replace("_open", "_var")

            def _make_liab_updater(_o=o_key, _c=c_key, _v=v_key):
                def _upd(*_):
                    try:
                        c_val = float(g(_c).get() or 0)
                        o_val = float(g(_o).get() or 0)
                        g(_v).set(str(int(c_val - o_val)))
                    except (ValueError, TypeError) as e:
                        logger.error(f"Liab calculation error: {e}")

                return _upd

            _lu = _make_liab_updater()
            if hasattr(fv, "register_trace"):
                fv.register_trace(g(o_key), "write", _lu)
                fv.register_trace(g(c_key), "write", _lu)
            else:
                g(o_key).trace_add("write", _lu)
                g(c_key).trace_add("write", _lu)
            table_data_row(
                f,
                idx,
                [
                    {
                        "text": lbl,
                        "font": Theme.BODY,
                        "text_color": Theme.TEXT_DIM,
                        "anchor": "w",
                        "weight": 2,
                    },
                    {
                        "textvariable": g(o_key),
                        "font": Theme.DATA,
                        "justify": "right",
                        **Theme.get_entry_style(),
                        "weight": 1,
                    },
                    {
                        "textvariable": g(c_key),
                        "font": Theme.DATA,
                        "justify": "right",
                        **Theme.get_entry_style(),
                        "weight": 1,
                    },
                    {
                        "textvariable": g(v_key),
                        "font": Theme.DATA,
                        "justify": "right",
                        "state": "readonly",
                        **Theme.get_entry_style("calc"),
                        "weight": 1,
                    },
                ],
            )
        ctk.CTkFrame(f, height=SPACING_MD, fg_color="transparent").pack()
        make_card(
            f,
            "ASSETS  (Comparative)",
            title_color=Theme.SUCCESS_GREEN,
            pady_bottom=2,
        )
        table_header_frame(
            f,
            [
                ("Asset", 2),
                ("Opening ₹", 1),
                ("Closing ₹", 1),
                ("Depreciation ₹", 1),
            ],
        )
        asset_items = [
            (
                "Sundry Debtors",
                "bp_asset_debtors_open",
                "bp_asset_debtors_close",
                "bp_asset_debtors_depr",
            ),
            (
                "Inventory",
                "bp_asset_inv_open",
                "bp_asset_inv_close",
                "bp_asset_inv_depr",
            ),
            (
                "Cash in Hand",
                "bp_asset_cash_open",
                "bp_asset_cash_close",
                "bp_asset_cash_depr",
            ),
            (
                "Bank Balances",
                "bp_asset_bank_open",
                "bp_asset_bank_close",
                "bp_asset_bank_depr",
            ),
            (
                "Loans & Advances",
                "bp_asset_loans_adv_open",
                "bp_asset_loans_adv_close",
                "bp_asset_loans_adv_depr",
            ),
        ]
        for idx, (lbl, o_key, c_key, d_key) in enumerate(asset_items):
            table_data_row(
                f,
                idx,
                [
                    {
                        "text": lbl,
                        "font": Theme.BODY,
                        "text_color": Theme.TEXT_DIM,
                        "anchor": "w",
                        "weight": 2,
                    },
                    {
                        "textvariable": g(o_key),
                        "font": Theme.DATA,
                        "justify": "right",
                        **Theme.get_entry_style(),
                        "weight": 1,
                    },
                    {
                        "textvariable": g(c_key),
                        "font": Theme.DATA,
                        "justify": "right",
                        **Theme.get_entry_style(),
                        "weight": 1,
                    },
                    {
                        "textvariable": g(d_key),
                        "font": Theme.DATA,
                        "justify": "right",
                        **Theme.get_entry_style(),
                        "weight": 1,
                    },
                ],
            )
        ctk.CTkFrame(f, height=SPACING_MD, fg_color="transparent").pack()
        make_card(f, "GST RECONCILIATION", pady_bottom=2)
        table_header_frame(
            f,
            [
                ("GSTIN", 2),
                ("Turnover (GST) ₹", 1),
                ("Turnover (Books) ₹", 1),
                ("Variance ₹", 1),
            ],
        )
        for i in range(10):

            def _make_gst_updater(_i=i):
                def _upd(*_):
                    try:
                        to = float(g(f"gst_{_i}_turnover").get() or 0)
                        inc = float(g(f"gst_{_i}_income").get() or 0)
                        g(f"gst_{_i}_var").set(str(int(to - inc)))
                    except (ValueError, TypeError) as e:
                        logger.error(f"GST calculation error: {e}")

                return _upd

            _gu = _make_gst_updater()
            if hasattr(fv, "register_trace"):
                fv.register_trace(g(f"gst_{i}_turnover"), "write", _gu)
                fv.register_trace(g(f"gst_{i}_income"), "write", _gu)
            else:
                g(f"gst_{i}_turnover").trace_add("write", _gu)
                g(f"gst_{i}_income").trace_add("write", _gu)
            table_data_row(
                f,
                i,
                [
                    {
                        "textvariable": g(f"gst_{i}_no", ""),
                        "font": Theme.DATA,
                        **Theme.get_entry_style(),
                        "weight": 2,
                    },
                    {
                        "textvariable": g(f"gst_{i}_turnover"),
                        "font": Theme.DATA,
                        "justify": "right",
                        **Theme.get_entry_style(),
                        "weight": 1,
                    },
                    {
                        "textvariable": g(f"gst_{i}_income"),
                        "font": Theme.DATA,
                        "justify": "right",
                        **Theme.get_entry_style(),
                        "weight": 1,
                    },
                    {
                        "textvariable": g(f"gst_{i}_var"),
                        "font": Theme.DATA,
                        "justify": "right",
                        "state": "readonly",
                        **Theme.get_entry_style("calc"),
                        "weight": 1,
                    },
                ],
            )
        ctk.CTkFrame(f, height=SPACING_MD, fg_color="transparent").pack()
        itr4_card = make_card(f, "ITR-4 MANDATORY DISCLOSURES (For AY 2026-27)")
        field_row(
            itr4_card, "Total Investment in Assets (Closing)", fv.get("itr4_investments")
        )
        field_row(itr4_card, "Total Bank Balance (Closing)", fv.get("itr4_bank_balance"))
        ctk.CTkFrame(f, height=SPACING_MD, fg_color="transparent").pack()
        ctk.CTkFrame(f, height=SPACING_MD, fg_color="transparent").pack()
        msme_card = make_card(f, "STATUTORY DISALLOWANCES (Section 43B & MSMED Act)")
        field_row(
            msme_card,
            "Delayed payments to MSME disallowed u/s 43B(h) (Principal)",
            fv.get("msme_43b_disallowance"),
        )
        field_row(
            msme_card,
            "Interest on delayed MSE payments inadmissible u/s 23 MSMED Act",
            fv.get("msme_interest_disallowance"),
        )
        from src.gui.widgets.common import info_banner

        info_banner(
            msme_card,
            "ℹ  MSME RULE",
            "Expenses for MSME payments delayed beyond 15/45 days (Principal) and any associated Interest are not deductible.",
            color=Theme.ACCENT_PRIMARY,
        )
        ctk.CTkFrame(f, height=SPACING_MD, fg_color="transparent").pack()
        sm = make_card(f, pady_bottom=16)
        ctk.CTkLabel(
            sm,
            text="TOTAL BUSINESS INCOME",
            font=Theme.H2,
            text_color=Theme.SUCCESS_GREEN,
            anchor="w"
        ).pack(side="left", padx=CARD_PADX, pady=SPACING_MD)
        ctk.CTkLabel(
            sm,
            textvariable=g("bp_total"),
            font=Theme.H1,
            text_color=Theme.SUCCESS_GREEN,
            anchor="e"
        ).pack(side="right", padx=CARD_PADX, pady=SPACING_MD)
        return f
