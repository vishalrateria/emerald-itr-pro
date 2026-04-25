import customtkinter as ctk
from src.gui.styles.theme import Theme
from src.gui.styles.constants import SPACING_SM, SPACING_MD, SPACING_LG
from src.gui.widgets.common import (
    page_header,
    make_card,
    card_spacer,
    field_row,
    static_field_row,
    info_banner,
)


class DeductionsSchedule:
    @staticmethod
    def create_frame(parent, fv, validation_refs=None):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        page_header(
            f,
            "DEDUCTIONS & EXEMPTIONS",
            "Chapter VI-A  |  AY 2026-27",
            accent_color=Theme.TTI_PURPLE,
        )

        opt = make_card(f, "SECTION 80C OPTIMIZER", accent_color=Theme.TTI_PURPLE)
        try:
            val_80c = float(fv.get("ded_80c", ctk.StringVar(value="0")).get() or 0)
            limit = 150000
            remaining = max(0, limit - val_80c)
            p_val = min(1.0, val_80c / limit)
            status = (
                f"Invested: ₹{int(val_80c):,}  |  Remaining Limit: ₹{int(remaining):,}"
                if remaining > 0
                else "✓ Maximum Limit of ₹1,50,000 Reached"
            )
            ctk.CTkLabel(
                opt,
                text=status,
                font=Theme.BODY_BOLD,
                text_color=Theme.SUCCESS_GREEN if remaining == 0 else Theme.TAX_AMBER,
            ).pack(pady=SPACING_SM)
            pb = ctk.CTkProgressBar(
                opt,
                width=400,
                height=8,
                fg_color=Theme.BG_INPUT,
                progress_color=Theme.TTI_PURPLE,
            )
            pb.set(p_val)
            pb.pack(pady=(0, SPACING_MD))
        except Exception:
            pass

        info_banner(
            f,
            "INFO: NEW REGIME RULES",
            "For AY 2026-27, Chapter VI-A has been streamlined. Most legacy deductions (80C, 80D) are only available under the Old Regime.",
            color=Theme.ACCENT_PRIMARY,
        )

        ded_card = make_card(f, "PERMISSIBLE DEDUCTIONS")
        static_field_row(
            ded_card,
            "Standard Deduction  u/s 16(ia)",
            "₹ 75,000  (Auto)",
            color=Theme.TEXT_DIM,
        )
        field_row(
            ded_card,
            "80CCD(2) — NPS Employer Contribution",
            fv["ded_80ccd2"],
            key="ded_80ccd2",
            validation_refs=validation_refs,
        )
        field_row(
            ded_card,
            "80JJAA — New / Additional Employees",
            fv["ded_80jjaa"],
            key="ded_80jjaa",
            validation_refs=validation_refs,
        )
        field_row(
            ded_card,
            "80CCH — Agniveer Corpus Fund",
            fv["ded_80cch"],
            key="ded_80cch",
            validation_refs=validation_refs,
        )
        card_spacer(ded_card)
        info_banner(
            f,
            "INFO: LEGISLATIVE REFERENCE",
            "Chapter VI-A has been simplified under Finance Act 2025. "
            "For AY 2026-27, only specific deductions apply under "
            "the default new regime.",
            color=Theme.TEXT_DIM,
        )
        return f
