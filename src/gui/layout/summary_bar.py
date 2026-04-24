import customtkinter as ctk
from src.gui.styles.constants import (
    SUMMARY_BAR_HEIGHT, SPACING_XL, SPACING_LG, SPACING_SM, SPACING_XS, DIVIDER_HEIGHT,
)
from src.gui.styles.theme import Theme
from src.services.logging_service import log as logger


class SummaryBarMixin:
    def _setup_summary_bar(self):
        self.summary_bar = ctk.CTkFrame(self, height=SUMMARY_BAR_HEIGHT, fg_color=Theme.BG_SECONDARY, corner_radius=0, border_width=0)
        ctk.CTkFrame(self, height=DIVIDER_HEIGHT, fg_color=Theme.SECTION_BORDER).grid(row=1, column=0, sticky="ew", pady=(0, SUMMARY_BAR_HEIGHT - DIVIDER_HEIGHT))
        self.summary_bar.grid(row=1, column=0, sticky="ew", pady=(DIVIDER_HEIGHT, 0))
        self.summary_bar.pack_propagate(False)
        self.summary_bar.grid_propagate(False)
        self._strip_labels = {}
        strip_items = [
            ("GTI", "strip_gti", Theme.GTI_BLUE),
            ("TTI", "strip_tti", Theme.TTI_PURPLE),
            ("TAX", "strip_tax", Theme.TAX_AMBER),
            ("NET", "strip_net", Theme.SUCCESS_GREEN)
        ]
        for i, (title, key, color) in enumerate(strip_items):
            if i > 0:
                ctk.CTkFrame(self.summary_bar, width=DIVIDER_HEIGHT, fg_color=Theme.SECTION_BORDER).pack(side="left", fill="y", padx=SPACING_SM)
            seg = ctk.CTkFrame(self.summary_bar, fg_color="transparent", cursor="hand2")
            seg.pack(side="left", padx=SPACING_XL, pady=0, expand=False)
            
            def _jump(e, k=key):
                self.show_frame("master")
            
            seg.bind("<Button-1>", _jump)
            seg.bind("<Enter>", lambda e, s=seg: s.configure(fg_color=Theme.BG_HOVER))
            seg.bind("<Leave>", lambda e, s=seg: s.configure(fg_color="transparent"))
            
            ctk.CTkLabel(seg, text=title, font=Theme.CAPTION, text_color=Theme.TEXT_MUTED).pack(side="left", padx=(0, SPACING_XS))
            lbl = ctk.CTkLabel(seg, text="₹ 0", font=Theme.BODY_BOLD, text_color=color)
            lbl.pack(side="left")
            self._strip_labels[key] = lbl
            
            for child in seg.winfo_children():
                child.bind("<Button-1>", _jump)
                child.bind("<Enter>", lambda e, s=seg: s.configure(fg_color=Theme.BG_HOVER))
                child.bind("<Leave>", lambda e, s=seg: s.configure(fg_color="transparent"))

        ctk.CTkLabel(self.summary_bar, text="AY 2026-27  ·  New Tax Regime", font=Theme.CAPTION, text_color=Theme.TEXT_DIM).pack(side="right", padx=SPACING_LG)

    def update_summary_strip(self):
        try:
            def _get_val(k):
                return float(self.vars[k].get() or 0)
            tax = _get_val("due_tax")
            paid = _get_val("it_total")
            self._ui_controller.update_status_bar(tax, paid)
            self._strip_labels["strip_gti"].configure(text=f"₹ {int(_get_val('gti')):,}")
            self._strip_labels["strip_tti"].configure(text=f"₹ {int(_get_val('tti')):,}")
            self._strip_labels["strip_tax"].configure(text=f"₹ {int(_get_val('due_tax')):,}")
            net = _get_val("due_tax") - _get_val("it_total")
            self._strip_labels["strip_net"].configure(text=f"₹ {int(net):,}", text_color=Theme.SUCCESS_GREEN if net <= 0 else Theme.ERROR_RED)
        except Exception as e:
            logger.debug(f"Summary strip update partial: {e}")
