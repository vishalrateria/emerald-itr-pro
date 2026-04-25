import customtkinter as ctk
from typing import Any, Callable
from tkinter import messagebox
from src.gui.styles.theme import Theme
from src.gui.styles.constants import (
    MODAL_WIDTH_SM,
    MODAL_HEIGHT_MD,
    BUTTON_HEIGHT_MD,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XS,
)


class DialogFactory:
    @staticmethod
    def show_tax_calendar(parent: Any) -> None:
        dialog = ctk.CTkToplevel(parent)
        dialog.title("Tax Calendar AY 2026-27")
        dialog.geometry(f"{MODAL_WIDTH_MD}x{MODAL_HEIGHT_MD}")
        dialog.attributes("-topmost", True)

        ctk.CTkLabel(
            dialog,
            text="📅 Upcoming Deadlines",
            font=Theme.H1,
            text_color=Theme.TEXT_PRIMARY,
        ).pack(pady=SPACING_LG)

        container = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=SPACING_LG, pady=SPACING_MD)

        deadlines = [
            ("June 15, 2025", "1st Installment Advance Tax"),
            ("July 31, 2025", "ITR Filing Deadline (Non-Audit)"),
            ("Sept 15, 2025", "2nd Installment Advance Tax"),
            ("Oct 31, 2025", "ITR Filing Deadline (Audit cases)"),
            ("Dec 15, 2025", "3rd Installment Advance Tax"),
            ("Mar 15, 2026", "Final Installment Advance Tax"),
        ]

        for date, desc in deadlines:
            frame = ctk.CTkFrame(container, fg_color=Theme.BG_INPUT)
            frame.pack(fill="x", pady=SPACING_XS)
            ctk.CTkLabel(
                frame, text=date, font=Theme.BODY_BOLD, width=120, anchor="w"
            ).pack(side="left", padx=SPACING_SM, pady=SPACING_SM)
            ctk.CTkLabel(frame, text=desc, font=Theme.BODY).pack(
                side="left", padx=SPACING_XS
            )

    @staticmethod
    def show_backup_menu(
        parent: Any, on_backup: Callable, on_restore: Callable
    ) -> None:
        menu = ctk.CTkToplevel(parent)
        menu.title("Backup & Restore")
        menu.geometry(f"{MODAL_WIDTH_SM}x{MODAL_HEIGHT_MD}")
        menu.attributes("-topmost", True)

        ctk.CTkLabel(
            menu,
            text="💾 Database Management",
            font=Theme.H2,
            text_color=Theme.TEXT_PRIMARY,
        ).pack(pady=SPACING_LG)

        ctk.CTkButton(
            menu,
            text="Create Manual Backup",
            command=on_backup,
            height=BUTTON_HEIGHT_MD,
            **Theme.get_button_style("primary"),
        ).pack(pady=SPACING_XS, padx=SPACING_LG, fill="x")
        ctk.CTkButton(
            menu,
            text="Restore from JSON/MCDB",
            command=on_restore,
            height=BUTTON_HEIGHT_MD,
            **Theme.get_button_style("secondary"),
        ).pack(pady=SPACING_XS, padx=SPACING_LG, fill="x")

    @staticmethod
    def show_sync_menu(parent: Any) -> None:
        menu = ctk.CTkToplevel(parent)
        menu.title("Sync with Portal")
        menu.geometry(f"{MODAL_WIDTH_SM}x{MODAL_HEIGHT_MD}")
        menu.attributes("-topmost", True)

        ctk.CTkButton(
            menu,
            text="🔄 Sync with IT Portal",
            command=lambda: messagebox.showinfo("Sync", "Connecting..."),
            height=BUTTON_HEIGHT_MD,
            **Theme.get_button_style("primary"),
        ).pack(pady=SPACING_SM, padx=SPACING_LG, fill="x")
        ctk.CTkButton(
            menu,
            text="📥 Download AIS/TIS",
            command=lambda: messagebox.showinfo("Download", "Fetching..."),
            height=BUTTON_HEIGHT_MD,
            **Theme.get_button_style("secondary"),
        ).pack(pady=SPACING_SM, padx=SPACING_LG, fill="x")
        ctk.CTkButton(
            menu,
            text="📤 Upload ITR JSON",
            command=lambda: messagebox.showinfo("Upload", "Preparing..."),
            height=BUTTON_HEIGHT_MD,
            **Theme.get_button_style("secondary"),
        ).pack(pady=SPACING_SM, padx=SPACING_LG, fill="x")
