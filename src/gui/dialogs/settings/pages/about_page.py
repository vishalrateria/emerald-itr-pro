import customtkinter as ctk
import sys
from src.config import APP_VERSION, BUILD_DATE, AY_CYCLE
from src.gui.styles.theme import Theme
from src.gui.styles.constants import SPACING_XS, SPACING_SM
from ..widgets.section_label import section_label


def build_page_about(dialog, p):
    section_label(p, "About Emerald ITR Pro")

    info = [
        ("Application", "Emerald ITR Pro"),
        ("Version", f"v{APP_VERSION}"),
        ("Build Date", BUILD_DATE),
        ("Assessment Year", AY_CYCLE),
        ("Tax Regime", "New Tax Regime (Section 115BAC)"),
        ("Engine", "ITREngine (Pure Python, Offline-First)"),
        ("Platform", sys.platform.capitalize()),
        ("Python Version",
         f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"),
        ("License", "Proprietary — All Rights Reserved"),
    ]
    for label, value in info:
        row = ctk.CTkFrame(p, fg_color="transparent")
        row.pack(fill="x", pady=SPACING_XS)
        row.grid_columnconfigure(0, weight=0, minsize=200)
        row.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(row, text=label, font=Theme.BODY_BOLD,
                     text_color=Theme.TEXT_DIM, anchor="w"
                     ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(row, text=value, font=Theme.BODY,
                     text_color=Theme.TEXT_PRIMARY, anchor="w"
                     ).grid(row=0, column=1, sticky="w")

    section_label(p, "Regulatory Compliance")
    ctk.CTkLabel(
        p,
        text=(
            "This application is compliant with Indian Income Tax provisions\n"
            "for FY 2025-26 (AY 2026-27) including Finance Act 2024/2025.\n\n"
            "Key provisions covered: Sections 115BAC, 87A, 207, 234A/B/C/F,\n"
            "111A, 112, 112A, 115BBH, 115BBJ, 44AD, 44ADA, 44AE."
        ),
        font=Theme.BODY, text_color=Theme.TEXT_DIM, anchor="w", justify="left",
        wraplength=480,
    ).pack(fill="x", pady=SPACING_SM)
