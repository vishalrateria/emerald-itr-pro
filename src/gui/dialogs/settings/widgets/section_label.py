import customtkinter as ctk
from src.gui.styles.theme import Theme
from src.gui.styles.constants import SPACING_MD, SPACING_XS, SPACING_SM


def section_label(parent, text: str):
    ctk.CTkLabel(
        parent, text=text, font=Theme.H3, text_color=Theme.TEXT_DIM, anchor="w"
    ).pack(fill="x", pady=(SPACING_MD, SPACING_XS))
    ctk.CTkFrame(parent, fg_color=Theme.SECTION_BORDER, height=1).pack(
        fill="x", pady=(0, SPACING_SM)
    )
