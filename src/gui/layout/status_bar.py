import customtkinter as ctk
from src.gui.styles.constants import (
    STATUS_BAR_HEIGHT,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XS,
    DIVIDER_HEIGHT,
)
from src.gui.styles.theme import Theme


class StatusBarMixin:
    def _setup_status_bar(self):
        self.status_bar = ctk.CTkFrame(
            self, height=STATUS_BAR_HEIGHT, fg_color=Theme.BG_SECONDARY, corner_radius=0
        )
        ctk.CTkFrame(self, height=DIVIDER_HEIGHT, fg_color=Theme.SECTION_BORDER).grid(
            row=3, column=0, sticky="ew"
        )
        self.status_bar.grid(row=4, column=0, sticky="ew")
        self.status_bar.pack_propagate(False)
        self.status_bar.grid_propagate(False)
        self.status_dot = ctk.CTkLabel(
            self.status_bar,
            text="●",
            font=Theme.ICON_SM,
            text_color=Theme.SUCCESS_GREEN,
        )
        self.status_dot.pack(side="left", padx=(SPACING_LG, 0))
        self.status_text = ctk.CTkLabel(
            self.status_bar,
            text="Engine Ready",
            font=Theme.CAPTION,
            text_color=Theme.TEXT_DIM,
        )
        self.status_text.pack(side="left", padx=(SPACING_XS, SPACING_MD))
        self.save_status_label = ctk.CTkLabel(
            self.status_bar, text="", font=Theme.CAPTION, text_color=Theme.TEXT_MUTED
        )
        self.save_status_label.pack(side="left")
        self.conn_label = ctk.CTkLabel(
            self.status_bar,
            text="● ONLINE",
            font=Theme.CAPTION,
            text_color=Theme.SUCCESS_GREEN,
        )
        self.conn_label.pack(side="right", padx=SPACING_LG)
        ctk.CTkLabel(
            self.status_bar,
            text=self.VERSION,
            font=Theme.CAPTION_BOLD,
            text_color=Theme.TEXT_MUTED,
        ).pack(side="right", padx=SPACING_MD)
        self.compute_progress = ctk.CTkProgressBar(
            self.status_bar,
            width=120,
            height=4,
            fg_color=Theme.BG_INPUT,
            progress_color=Theme.ACCENT_PRIMARY,
        )
        self.compute_progress.set(0)
