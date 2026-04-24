from src.gui.styles.constants import SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG, CARD_PADX, INNER_PADX, BUTTON_HEIGHT_SM, ICON_BUTTON_WIDTH_SM, DIVIDER_HEIGHT
import customtkinter as ctk
from src.gui.styles.theme import Theme
from src.gui.widgets.common import (
    page_header,
    make_card,
    summary_row,
)


class MasterSchedule:
    @staticmethod
    def create_frame(parent, fv, sf, sl):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        page_header(f, "MASTER COMPUTATION DASHBOARD",
                    "Final Review of Income Sources & Tax Liability", accent_color=Theme.GTI_BLUE)

        banner = make_card(f, pady_bottom=SPACING_SM)
        banner.pack_forget()
        banner.pack(fill="x", padx=CARD_PADX, pady=(SPACING_LG, SPACING_SM))
        banner_info = ctk.CTkFrame(banner, fg_color="transparent")
        banner_info.pack(side="left", padx=CARD_PADX, pady=SPACING_SM)

        sl["m_banner_text"] = ctk.CTkLabel(
            banner_info, text="AY 2026-27  ·  NEW TAX REGIME", font=Theme.H3, text_color=Theme.TEXT_DIM, anchor="w")
        sl["m_banner_text"].pack(fill="x")
        sl["m_banner_tip"] = ctk.CTkLabel(banner_info, text="Tip: Enter Salary/Business details to see tax impact",
                                          font=Theme.CAPTION, text_color=Theme.ACCENT_PRIMARY, anchor="w")
        sl["m_banner_tip"].pack(fill="x")

        sl["tax_net_banner"] = ctk.CTkLabel(
            banner, text="PAYABLE:  ₹ 0", font=Theme.H1, text_color=Theme.ERROR_RED, anchor="e")
        sl["tax_net_banner"].pack(side="right", padx=CARD_PADX, pady=SPACING_MD)

        grid = ctk.CTkFrame(f, fg_color="transparent")
        grid.pack(fill="x", padx=CARD_PADX, pady=(0, SPACING_MD))
        grid.columnconfigure(0, weight=1, pad=6)
        grid.columnconfigure(1, weight=1, pad=6)
        grid.rowconfigure(0, weight=1)
        left = make_card(grid, "INCOME SOURCES", pady_bottom=0, accent_color=Theme.GTI_BLUE, hover=True)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING_XS))

        inc_container = ctk.CTkFrame(left, fg_color="transparent")
        inc_container.pack(fill="both", expand=True, padx=2)
        inc_container.grid_columnconfigure(0, weight=1)
        summary_row(inc_container, 0, "1. Salary Income", "sal", "row_sal",
                    sl, status_key="sal", edit_target="salary", switch_fn=sf)
        summary_row(inc_container, 1, "2. House Property", "hp_total", "row_hp_total",
                    sl, status_key="hp", edit_target="hp", switch_fn=sf)
        summary_row(inc_container, 2, "3. Business & Profession", "bp_total", "row_bp_total",
                    sl, status_key="bp", edit_target="business_financials", switch_fn=sf)
        summary_row(inc_container, 3, "4. STCG (Real Estate/Others)", "stcg_sum",
                    "row_stcg_sum", sl, status_key="stcg", edit_target="stcg", switch_fn=sf)
        summary_row(inc_container, 4, "5. LTCG (112A/Others)", "ltcg_112a_sum",
                    "row_ltcg_112a_sum", sl, status_key="ltcg", edit_target="ltcg", switch_fn=sf)
        summary_row(inc_container, 5, "6. VDA (Crypto/NFT) @ 30%", "vda_sum",
                    "row_vda_sum", sl, status_key="vda", edit_target="vda", switch_fn=sf)
        summary_row(inc_container, 6, "7. Income from Other Sources", "os_total",
                    "row_os_total", sl, status_key="os", edit_target="other_sources", switch_fn=sf)

        ctk.CTkFrame(left, height=DIVIDER_HEIGHT, fg_color=Theme.SECTION_BORDER).pack(
            fill="x", padx=INNER_PADX, pady=(SPACING_SM, 0))
        summary_row(left, 8, "8. GROSS TOTAL INCOME", "gti", "row_gti", sl)
        summary_row(left, 9, "9. Total Deductions (Ch. VI-A)", "ded_total", "row_ded_total", sl)
        summary_row(left, 10, "10. TOTAL TAXABLE INCOME", "tti", "row_tti", sl)

        gti_row = ctk.CTkFrame(left, fg_color=Theme.BG_INPUT, corner_radius=8)
        gti_row.pack(fill="x", padx=INNER_PADX, pady=(SPACING_XS, SPACING_MD))
        gti_row.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            gti_row,
            text="GROSS TOTAL INCOME (GTI)",
            font=Theme.BODY_BOLD,
            text_color=Theme.TEXT_PRIMARY,
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=INNER_PADX, pady=SPACING_SM)
        gti_lbl = ctk.CTkLabel(
            gti_row,
            text="₹ 0",
            font=Theme.H2,
            text_color=Theme.ACCENT_PRIMARY,
            anchor="e",
        )
        gti_lbl.grid(row=0, column=1, sticky="e", padx=INNER_PADX, pady=SPACING_SM)
        sl["gti_banner"] = gti_lbl
        right = make_card(grid, "TAX COMPUTATION", pady_bottom=0, title_color=Theme.TEXT_DIM, accent_color=Theme.TAX_AMBER, hover=True)
        right.pack_forget()
        right.grid(row=0, column=1, sticky="nsew", padx=(SPACING_XS, 0))
        tax_container = ctk.CTkFrame(right, fg_color="transparent")

        def _tax_row(lbl, sum_key, row_idx=0, color=None, target=None, bold=False):
            if row_idx >= 0:
                row = ctk.CTkFrame(tax_container, fg_color="transparent",
                                   corner_radius=Theme.RADIUS_SM)
                row.grid(row=row_idx, column=0, sticky="ew", padx=INNER_PADX, pady=1)
                row.bind("<Enter>", lambda e: row.configure(fg_color=Theme.BG_INPUT))
                row.bind("<Leave>", lambda e: row.configure(fg_color="transparent"))
            else:
                row = ctk.CTkFrame(right, fg_color="transparent", corner_radius=Theme.RADIUS_SM)
                row.pack(fill="x", padx=INNER_PADX, pady=SPACING_XS)
                row.bind("<Enter>", lambda e: row.configure(fg_color=Theme.BG_INPUT))
                row.bind("<Leave>", lambda e: row.configure(fg_color="transparent"))
            sl[f"row_{sum_key}"] = row

            fnt = Theme.BODY_BOLD if bold else Theme.BODY
            lbl_w = ctk.CTkLabel(
                row, text=lbl, font=fnt, text_color=Theme.TEXT_DIM, anchor="w", justify="left"
            )
            lbl_w.grid(row=0, column=0, sticky="ew", padx=SPACING_SM, pady=SPACING_XS)
            col = 1
            if target:
                ctk.CTkButton(
                    row,
                    text="EDIT",
                    width=ICON_BUTTON_WIDTH_SM,
                    height=BUTTON_HEIGHT_SM,
                    font=Theme.CAPTION,
                    command=lambda t=target: sf(t),
                    **Theme.get_button_style("secondary"),
                ).grid(row=0, column=col, sticky="e", padx=SPACING_XS, pady=SPACING_XS)
                col += 1
            val_lbl = ctk.CTkLabel(
                row,
                text="₹ 0",
                font=Theme.BODY_BOLD if bold else Theme.BODY,
                text_color=color or Theme.TEXT_PRIMARY,
                anchor="e",
            )
            val_lbl.grid(row=0, column=col, sticky="e", padx=INNER_PADX, pady=SPACING_XS)
            sl[sum_key] = val_lbl
            return val_lbl

        def _highlighted_row(right_frame, lbl, sum_key, color):
            row = ctk.CTkFrame(right_frame, fg_color=Theme.BG_INPUT, corner_radius=8)
            row.pack(fill="x", padx=INNER_PADX, pady=(SPACING_XS, 0))
            row.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                row,
                text=lbl,
                font=Theme.BODY_BOLD,
                text_color=Theme.TEXT_PRIMARY,
                anchor="w",
            ).grid(row=0, column=0, sticky="w", padx=INNER_PADX, pady=SPACING_SM)
            lbl_w = ctk.CTkLabel(
                row, text="₹ 0", font=Theme.H2, text_color=color, anchor="e"
            )
            lbl_w.grid(row=0, column=1, sticky="e", padx=INNER_PADX, pady=SPACING_SM)
            sl[sum_key] = lbl_w
            sl[f"row_{sum_key}"] = row
            return lbl_w

        def _divider(frame):
            ctk.CTkFrame(frame, height=DIVIDER_HEIGHT, fg_color=Theme.SECTION_BORDER).pack(
                fill="x", padx=INNER_PADX, pady=(SPACING_XS, SPACING_XS)
            )

        _tax_row(
            "Chapter VI-A Deductions",
            "ded_total",
            row_idx=-1,
            color=Theme.TEXT_DIM,
            target="deductions",
        )
        _highlighted_row(
            right, "TOTAL TAXABLE INCOME (TTI)", "tti_banner", Theme.SUCCESS_GREEN
        )
        ctk.CTkFrame(right, height=SPACING_SM, fg_color="transparent").pack()
        ctk.CTkLabel(
            right,
            text="TAX BREAKDOWN",
            font=Theme.CAPTION,
            text_color=Theme.TEXT_DIM,
            anchor="w",
        ).pack(fill="x", padx=CARD_PADX, pady=(SPACING_XS, SPACING_XS))
        _divider(right)

        tax_container.pack(fill="x", padx=SPACING_XS)
        tax_container.grid_columnconfigure(0, weight=1)
        for i in range(12):
            tax_container.grid_rowconfigure(i, weight=1)

        _tax_row("Slab Tax (New Regime)", "slab_tax", 0)
        _tax_row("87A Rebate / Relief", "rebate_87a", 1, color=Theme.SUCCESS_GREEN)
        _tax_row("LTCG Tax @ 12.5%", "ltcg_tax", 2)
        _tax_row("STCG Tax @ 20%", "stcg_tax", 3)
        _tax_row("VDA Tax @ 30%", "vda_tax", 4)
        _tax_row("Winnings Tax @ 30%", "winnings_tax", 5)
        _tax_row("Surcharge", "surcharge", 6)
        _tax_row("Health & Ed. Cess @ 4%", "cess", 7)
        _tax_row("Late Fee u/s 234F", "late_fee_234f", 8, color=Theme.ERROR_RED)
        _tax_row("Interest u/s 234A/B/C", "interest_total", 9, color=Theme.ERROR_RED)
        ctk.CTkFrame(right, fg_color="transparent").pack(fill="both", expand=True)
        _divider(right)
        _tax_row(
            "TOTAL TAX PAYABLE",
            "tax_total",
            row_idx=-1,
            color=Theme.ERROR_RED,
            bold=True,
        )
        _tax_row(
            "Tax Paid (TDS + TCS + Adv)",
            "it_total",
            row_idx=-1,
            color=Theme.TEXT_DIM,
            target="tax",
        )
        _divider(right)
        net_row = ctk.CTkFrame(right, fg_color=Theme.BG_INPUT, corner_radius=8)
        net_row.pack(fill="x", padx=INNER_PADX, pady=(SPACING_XS, SPACING_MD))
        net_row.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            net_row,
            text="NET PAYABLE / (REFUND)",
            font=Theme.BODY_BOLD,
            text_color=Theme.TEXT_PRIMARY,
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=INNER_PADX, pady=SPACING_SM)
        net_lbl = ctk.CTkLabel(
            net_row,
            text="₹ 0",
            font=Theme.H2,
            text_color=Theme.ACCENT_PRIMARY,
            anchor="e",
        )
        net_lbl.grid(row=0, column=1, sticky="e", padx=INNER_PADX, pady=SPACING_SM)
        sl["tax_net"] = net_lbl
        sl["row_tax_net"] = net_row
        sl["tax_due"] = sl["tax_total"]

        diag = make_card(f, "STATUTORY AUDIT & DIAGNOSTICS", pady_bottom=SPACING_LG, title_color=Theme.TEXT_DIM, accent_color=Theme.TTI_PURPLE, hover=True)

        sl["audit_log"] = ctk.CTkFrame(
            diag,
            fg_color="transparent"
        )
        sl["audit_log"].pack(fill="x", padx=INNER_PADX, pady=SPACING_SM)

        return f
