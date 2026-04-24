import customtkinter as ctk
from tkinter import filedialog
from src.gui.styles.theme import Theme
from src.gui.styles.constants import (
    DROPDOWN_WIDTH_SM,
    ENTRY_HEIGHT,
    ICON_BUTTON_WIDTH_SM,
    SPACING_XS,
)
from .form_row import create_row


def create_path_row(parent, label: str, var: ctk.StringVar, mode="file") -> ctk.CTkEntry:
    row = create_row(parent, label)
    inner = ctk.CTkFrame(row, fg_color="transparent")
    inner.grid(row=0, column=1, sticky="e")
    e = ctk.CTkEntry(inner, textvariable=var,
                     width=DROPDOWN_WIDTH_SM, height=ENTRY_HEIGHT,
                     font=Theme.BODY, justify="left", **Theme.get_entry_style())
    e.pack(side="left", padx=(0, SPACING_XS))

    def browse():
        if mode == "file":
            p = filedialog.askopenfilename(filetypes=[("Database", "*.mcdb"),
                                                      ("All", "*.*")])
        else:
            p = filedialog.askdirectory()
        if p:
            var.set(p)

    ctk.CTkButton(inner, text="…", width=ICON_BUTTON_WIDTH_SM, height=ENTRY_HEIGHT,
                  font=Theme.BODY_BOLD, command=browse,
                  **Theme.get_button_style("secondary")).pack(side="left")
    return e
