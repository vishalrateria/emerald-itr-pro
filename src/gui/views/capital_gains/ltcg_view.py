from src.config import (
    MAX_ENTRIES_CG
)
from src.gui.styles.constants import (
    SPACING_MD,
)
import customtkinter as ctk
from src.gui.styles.theme import Theme
from src.gui.widgets.common import (
    page_header,
    make_card,
    total_row,
    FluentTable,
)


class LTCGSchedule:
    @staticmethod
    def create_frame(parent, fv, sl, validation_refs=None):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        page_header(
            f,
            "SCHEDULE 112A — LONG-TERM CAPITAL GAINS",
            "LTCG on listed equity / equity MF | "
            "Taxable @ 12.5% above ₹1.25 Lakh exemption",
        )

        def ltcg_row_gen(i):
            return [
                {"textvariable": fv[f"ltcg112a_{i}_isin"], "key": f"ltcg112a_{i}_isin",
                    "font": Theme.DATA, **Theme.get_entry_style(), "weight": 1},
                {"textvariable": fv[f"ltcg112a_{i}_name"], "key": f"ltcg112a_{i}_name",
                    "font": Theme.BODY, **Theme.get_entry_style(), "weight": 2},
                {"textvariable": fv[f"ltcg112a_{i}_sale"], "key": f"ltcg112a_{i}_sale",
                    "font": Theme.DATA, "justify": "right", **Theme.get_entry_style(), "weight": 1},
                {"textvariable": fv[f"ltcg112a_{i}_cost"], "key": f"ltcg112a_{i}_cost",
                    "font": Theme.DATA, "justify": "right", **Theme.get_entry_style(), "weight": 1},
                {"textvariable": fv[f"ltcg112a_{i}_fmv"], "key": f"ltcg112a_{i}_fmv",
                    "font": Theme.DATA, "justify": "right", **Theme.get_entry_style(), "weight": 1},
                {"textvariable": fv[f"ltcg112a_{i}_gain"], "font": Theme.DATA, "justify": "right",
                    "state": "readonly", **Theme.get_entry_style("calc"), "weight": 1},
            ]

        FluentTable(
            f,
            "TRANSACTION-WISE LTCG",
            [("ISIN", 1), ("Scrip / Fund Name", 2), ("Sale Price ₹", 1),
             ("Cost ₹", 1), ("FMV ₹", 1), ("Gain ₹", 1)],
            MAX_ENTRIES_CG,
            ltcg_row_gen,
            validation_refs=validation_refs
        )
        ctk.CTkFrame(f, height=SPACING_MD, fg_color="transparent").pack()
        ctk.CTkFrame(f, height=SPACING_MD, fg_color="transparent").pack()
        bb_card = make_card(f, "BUYBACK LOSS REPORTING (Budget 2024)")
        from src.gui.widgets.common import field_row, card_spacer, info_banner

        info_banner(
            f,
            "ℹ  COMPLIANCE",
            "Buyback proceeds are now taxed as DIVIDEND in Sch OS. Enter COST here to claim Capital Loss.",
            color=Theme.BRAND_BLUE,
        )
        field_row(bb_card, "Company Name", fv.get("buyback_company"))
        field_row(bb_card, "Number of Shares", fv.get("buyback_shares"))
        field_row(bb_card, "Cost of Acquisition ₹", fv.get("buyback_cost"))
        field_row(bb_card, "Sale Consideration  ₹", fv.get("buyback_price"))
        card_spacer(bb_card)
        field_row(bb_card, "Date of Acquisition (DD-MM-YYYY)", fv.get("buyback_acq_date"))
        field_row(bb_card, "Date of Buyback (DD-MM-YYYY)", fv.get("buyback_date"))

        ctk.CTkFrame(f, height=SPACING_MD, fg_color="transparent").pack()
        other_112_card = make_card(f, "OTHER LTCG (Section 112)")
        info_banner(
            f,
            "ℹ  SECTION 112",
            "Applies to Land, Buildings, Unlisted Shares, etc. Taxable @ 12.5% (Budget 2024).",
            color=Theme.ACCENT_PRIMARY
        )
        field_row(other_112_card, "LTCG on Land / Buildings / Unlisted Shares ₹",
                  fv["ltcg_112_input"])
        field_row(other_112_card, "Exemption u/s 54 / 54F / 54EC ₹", fv["ltcg_112_exemption"])
        card_spacer(other_112_card)

        info_banner(
            f,
            "🛡️ TRANSITIONAL RELIEF",
            "For property acquired on/before 22-July-2024, enter details below to calculate the lower tax benefit.",
            color=Theme.ACCENT_PRIMARY
        )
        relief_card = make_card(f, "TRANSITIONAL RELIEF CALCULATION (Land/Building)")
        field_row(relief_card, "Sale Consideration ₹", fv["ltcg_prop_sale"])
        field_row(relief_card, "Cost of Acquisition ₹", fv["ltcg_prop_cost"])
        field_row(relief_card, "Date of Acquisition (DD-MM-YYYY)", fv["ltcg_prop_acq_date"])
        field_row(relief_card, "Indexation Cost (if any) ₹", fv["ltcg_prop_index_cost"])
        field_row(relief_card, "Recommended Relief Amount ₹",
                  fv["ltcg_prop_relief_amt"], state="readonly")

        ctk.CTkFrame(f, height=SPACING_MD, fg_color="transparent").pack()
        tot_card = make_card(f, pady_bottom=16)
        total_row(
            tot_card,
            "TOTAL LTCG  (u/s 112A)",
            "ltcg_112a_sum",
            sl,
            color=Theme.SUCCESS_GREEN,
        )

        q_card = make_card(f, "QUARTERLY BREAKUP OF CAPITAL GAINS (FOR 234C RELAXATION)")
        info_banner(
            f,
            "🛡️ 234C INTEREST PROTECTION",
            "Enter the portion of TOTAL capital gains (STCG + LTCG) earned in each quarter to avoid interest on gains not yet realized.",
            color=Theme.SUCCESS_GREEN
        )
        field_row(q_card, "Up to June 15", fv.get("cg_q1_jun15"))
        field_row(q_card, "June 16 to Sept 15", fv.get("cg_q2_sep15"))
        field_row(q_card, "Sept 16 to Dec 15", fv.get("cg_q3_dec15"))
        field_row(q_card, "Dec 16 to March 15", fv.get("cg_q4_mar15"))

        return f
