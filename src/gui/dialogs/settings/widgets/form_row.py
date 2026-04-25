import customtkinter as ctk
from src.gui.styles.theme import Theme
from src.gui.styles.constants import SPACING_XS, SPACING_MD, ENTRY_HEIGHT


def create_row(parent, label: str):
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", pady=SPACING_XS)
    row.grid_columnconfigure(0, weight=0, minsize=260)
    row.grid_columnconfigure(1, weight=1)
    ctk.CTkLabel(
        row, text=label, font=Theme.BODY, text_color=Theme.TEXT_PRIMARY, anchor="w"
    ).grid(row=0, column=0, sticky="w", padx=(0, SPACING_MD))
    return row


def create_entry(
    parent, label: str, var: ctk.StringVar, placeholder="", width=250
) -> ctk.CTkEntry:
    row = create_row(parent, label)
    e = ctk.CTkEntry(
        row,
        textvariable=var,
        placeholder_text=placeholder,
        width=width,
        height=ENTRY_HEIGHT,
        font=Theme.BODY,
        justify="left",
        **Theme.get_entry_style()
    )
    e.grid(row=0, column=1, sticky="w")
    return e


def create_combo(
    parent, label: str, var: ctk.StringVar, values: list, width=250
) -> ctk.CTkComboBox:
    row = create_row(parent, label)
    c = ctk.CTkComboBox(
        row,
        variable=var,
        values=values,
        width=width,
        height=ENTRY_HEIGHT,
        font=Theme.BODY,
        state="readonly",
        **Theme.get_combo_style()
    )
    c.grid(row=0, column=1, sticky="w")
    return c


def create_toggle(parent, label: str, var: ctk.BooleanVar) -> ctk.CTkSwitch:
    row = create_row(parent, label)
    s = ctk.CTkSwitch(
        row,
        variable=var,
        text="",
        onvalue=True,
        offvalue=False,
        progress_color=Theme.ACCENT_PRIMARY,
        button_color=Theme.TEXT_PRIMARY,
        fg_color=Theme.SECTION_BORDER,
    )
    s.grid(row=0, column=1, sticky="w")
    return s
