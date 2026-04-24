from src.gui.styles.constants import (
    SPACING_XS, SPACING_SM, SPACING_MD, CARD_PADX, INNER_PADX, 
    BUTTON_HEIGHT_SM, ENTRY_HEIGHT, TOOLTIP_DELAY_MS, ICON_BUTTON_WIDTH_SM,
    DIVIDER_HEIGHT
)
import customtkinter as ctk
from src.gui.styles.theme import Theme
import tkinter as tk

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.id = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(TOOLTIP_DELAY_MS, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        try:
            x, y, cx, cy = self.widget.bbox("insert")
            x = x + self.widget.winfo_rootx() + 27
            y = y + cy + self.widget.winfo_rooty() + 27
        except (AttributeError, tk.TclError):
            x = self.widget.winfo_rootx() + 27
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 27
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify="left", background=Theme.BG_INPUT, foreground=Theme.TEXT_PRIMARY,
                         relief="flat", borderwidth=1, font=Theme.CAPTION, padx=SPACING_XS, pady=SPACING_XS)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

def add_tooltip(widget: tk.Widget, text: str) -> None:
    if text:
        ToolTip(widget, text)

def page_header(parent, title: str, subtitle: str = "", accent_color: str = None):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    f.pack(fill="x", padx=CARD_PADX, pady=(SPACING_SM, SPACING_MD))
    if accent_color:
        indicator = ctk.CTkFrame(f, width=4, fg_color=accent_color, corner_radius=2)
        indicator.pack(side="left", fill="y", padx=(0, SPACING_MD))
    content = ctk.CTkFrame(f, fg_color="transparent")
    content.pack(side="left", fill="x", expand=True)
    ctk.CTkLabel(content, text=title, font=Theme.H1, text_color=Theme.TEXT_PRIMARY, anchor="w", justify="left").pack(anchor="w", fill="x")
    if subtitle:
        ctk.CTkLabel(content, text=subtitle, font=Theme.BODY, text_color=Theme.TEXT_DIM, anchor="w", justify="left").pack(anchor="w", fill="x", pady=(SPACING_XS, 0))

class CollapsibleSection(ctk.CTkFrame):
    def __init__(self, parent, title, is_open=True):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="x", padx=CARD_PADX, pady=(0, SPACING_SM))
        self.is_open = is_open
        self.header = ctk.CTkFrame(self, fg_color=Theme.BG_INPUT, height=BUTTON_HEIGHT_SM + 4, corner_radius=Theme.RADIUS_MD, border_width=1, border_color=Theme.SECTION_BORDER)
        self.header.pack(fill="x")
        self.title_lbl = ctk.CTkLabel(self.header, text=("▼  " if is_open else "▶  ") + title.upper(), font=Theme.CAPTION_BOLD, text_color=Theme.BRAND_BLUE, anchor="w")
        self.title_lbl.pack(side="left", padx=INNER_PADX, pady=2)
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        if is_open:
            self.content.pack(fill="x", pady=(SPACING_SM, 0))
        def _toggle(*args):
            self.toggle()
        self.header.bind("<Button-1>", _toggle)
        self.title_lbl.bind("<Button-1>", _toggle)
        def _on_header_enter(*args):
            self.header.configure(fg_color=Theme.BG_HOVER)
        def _on_header_leave(*args):
            self.header.configure(fg_color=Theme.BG_INPUT)
        self.header.bind("<Enter>", _on_header_enter)
        self.header.bind("<Leave>", _on_header_leave)
        self.title_lbl.bind("<Enter>", _on_header_enter)
        self.title_lbl.bind("<Leave>", _on_header_leave)

    def toggle(self):
        self.is_open = not self.is_open
        indicator = "▼  " if self.is_open else "▶  "
        self.title_lbl.configure(text=indicator + self.title_lbl.cget("text")[3:])
        if self.is_open:
            self.content.pack(fill="x", pady=(SPACING_SM, 0))
        else:
            self.content.pack_forget()

def field_row(parent: ctk.CTkFrame, label: str, var: tk.Variable, variant: str = "normal", state: str = "normal", key: str = None, validation_refs: dict = None, tooltip: str = None) -> ctk.CTkEntry:
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", padx=INNER_PADX, pady=(0, SPACING_SM))
    row.grid_columnconfigure(0, weight=3)
    row.grid_columnconfigure(1, weight=2, minsize=150)
    lbl = ctk.CTkLabel(row, text=label, font=Theme.BODY, text_color=Theme.TEXT_DIM, anchor="w", justify="left")
    lbl.grid(row=0, column=0, sticky="ew", padx=(0, SPACING_SM))
    e = ctk.CTkEntry(row, height=ENTRY_HEIGHT, textvariable=var, font=Theme.DATA, justify="right", state=state, **Theme.get_entry_style(variant))
    e.grid(row=0, column=1, sticky="ew")
    def _next_focus(event):
        event.widget.tk_focusNext().focus()
        return "break"
    def _on_focus(event):
        event.widget.configure(border_color=Theme.ACCENT_PRIMARY, border_width=1)
    def _on_blur(event):
        event.widget.configure(border_color=Theme.SECTION_BORDER, border_width=1)
    e.bind("<Return>", _next_focus)
    e.bind("<FocusIn>", _on_focus)
    e.bind("<FocusOut>", _on_blur)
    if key and validation_refs is not None:
        validation_refs[key] = e
    if tooltip:
        add_tooltip(lbl, tooltip)
        add_tooltip(e, tooltip)
    return e

def static_field_row(parent: ctk.CTkFrame, label: str, value: str, color: str = Theme.TEXT_PRIMARY, variant: str = "calc") -> None:
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", padx=INNER_PADX, pady=(0, SPACING_SM))
    row.grid_columnconfigure(0, weight=3)
    row.grid_columnconfigure(1, weight=2, minsize=150)
    ctk.CTkLabel(row, text=label, font=Theme.BODY, text_color=Theme.TEXT_DIM, anchor="w", justify="left").grid(row=0, column=0, sticky="ew", padx=(0, SPACING_SM))
    e = ctk.CTkEntry(row, height=ENTRY_HEIGHT, font=Theme.DATA, justify="right", text_color=color, state="readonly", **Theme.get_entry_style(variant))
    e.insert(0, value)
    e.grid(row=0, column=1, sticky="ew")

def total_row(parent: ctk.CTkFrame, label: str, key: str = None, summary_labels: dict = None, color: str = None) -> ctk.CTkLabel:
    row = ctk.CTkFrame(parent, fg_color=Theme.BG_INPUT, corner_radius=Theme.RADIUS_MD)
    row.pack(fill="x", padx=INNER_PADX, pady=(SPACING_SM, SPACING_SM))
    row.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(row, text=label, font=Theme.BODY_BOLD, text_color=Theme.TEXT_PRIMARY, anchor="w", justify="left").grid(row=0, column=0, sticky="w", padx=INNER_PADX, pady=SPACING_SM)
    lbl = ctk.CTkLabel(row, text="₹ 0", font=Theme.H2, text_color=color or Theme.SUCCESS_GREEN, anchor="e")
    lbl.grid(row=0, column=1, sticky="e", padx=INNER_PADX, pady=SPACING_SM)
    if key and summary_labels is not None:
        summary_labels[key] = lbl
    return lbl

def table_header_frame(parent, columns: list):
    h = ctk.CTkFrame(parent, fg_color=Theme.BG_INPUT, corner_radius=Theme.RADIUS_MD)
    h.pack(fill="x", padx=CARD_PADX, pady=(0, SPACING_XS))
    for i, (text, weight) in enumerate(columns):
        h.grid_columnconfigure(i, weight=weight)
        ctk.CTkLabel(h, text=text, font=Theme.BODY_BOLD, text_color=Theme.TEXT_DIM, anchor="w" if i == 0 else "e").grid(row=0, column=i, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")

def table_data_row(parent, row_idx, entries: list, validation_refs=None):
    bg = Theme.BG_SECONDARY if row_idx % 2 == 0 else "transparent"
    r = ctk.CTkFrame(parent, fg_color=bg, corner_radius=0)
    r.pack(fill="x", padx=CARD_PADX)
    for i, raw_cfg in enumerate(entries):
        e_cfg = dict(raw_cfg)
        weight = e_cfg.pop("weight", 1)
        key = e_cfg.pop("key", None)
        tooltip = e_cfg.pop("tooltip", None)
        r.grid_columnconfigure(i, weight=weight)
        if "text" in e_cfg and "textvariable" not in e_cfg and "values" not in e_cfg:
            e_cfg.setdefault("anchor", "w")
            e_cfg.setdefault("font", Theme.BODY)
            w = ctk.CTkLabel(r, **e_cfg)
        elif "values" in e_cfg:
            e_cfg.setdefault("font", Theme.BODY)
            e_cfg.update(Theme.get_combo_style())
            w = ctk.CTkComboBox(r, height=BUTTON_HEIGHT_SM, **e_cfg)
        else:
            e_cfg.setdefault("fg_color", "transparent")
            e_cfg.setdefault("border_width", 0)
            e_cfg.setdefault("corner_radius", 0)
            e_cfg.setdefault("height", BUTTON_HEIGHT_SM)
            e_cfg.setdefault("justify", "right")
            e_cfg.setdefault("font", Theme.DATA)
            w = ctk.CTkEntry(r, **e_cfg)
            if key and validation_refs is not None:
                validation_refs[key] = w
            
            def _on_focus_table(event, widget=w):
                widget.configure(border_width=1, border_color=Theme.ACCENT_PRIMARY)
            def _on_blur_table(event, widget=w):
                widget.configure(border_width=0)
            
            if isinstance(w, ctk.CTkEntry):
                w.bind("<FocusIn>", _on_focus_table)
                w.bind("<FocusOut>", _on_blur_table)
        w.grid(row=0, column=i, padx=SPACING_XS, pady=SPACING_XS, sticky="ew")
        if tooltip:
            add_tooltip(w, tooltip)

class FluentTable(ctk.CTkFrame):
    def __init__(self, parent, title, columns, max_rows, row_generator_fn, validation_refs=None):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="x", pady=(0, SPACING_MD), padx=CARD_PADX)
        if title:
            ctk.CTkLabel(self, text=title.upper(), font=Theme.H3, text_color=Theme.BRAND_BLUE, anchor="w").pack(padx=0, pady=(0, SPACING_SM), anchor="w")
        table_header_frame(self, columns)
        for i in range(max_rows):
            entries = row_generator_fn(i)
            table_data_row(self, i, entries, validation_refs=validation_refs)

def combo_field_row(parent: ctk.CTkFrame, label: str, var: ctk.StringVar, values: list, entry_minsize: int = 200, tooltip: str = None) -> ctk.CTkComboBox:
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", padx=INNER_PADX, pady=(0, SPACING_SM))
    row.grid_columnconfigure(0, weight=3)
    row.grid_columnconfigure(1, weight=2, minsize=entry_minsize)
    lbl = ctk.CTkLabel(row, text=label, font=Theme.BODY, text_color=Theme.TEXT_DIM, anchor="w", justify="left")
    lbl.grid(row=0, column=0, sticky="ew", padx=(0, SPACING_SM))
    c = ctk.CTkComboBox(row, values=values, variable=var, height=ENTRY_HEIGHT, font=Theme.BODY, **Theme.get_combo_style())
    def _on_focus(event):
        c.configure(border_color=Theme.ACCENT_PRIMARY)
    def _on_blur(event):
        c.configure(border_color=Theme.SECTION_BORDER)
    c.bind("<FocusIn>", _on_focus)
    c.bind("<FocusOut>", _on_blur)
    c.grid(row=0, column=1, sticky="ew")
    if tooltip:
        add_tooltip(lbl, tooltip)
        add_tooltip(c, tooltip)
    return c

def make_card(parent: ctk.CTkFrame, title: str = "", pady_bottom: int = 10, title_color: str = None, accent_color: str = None, hover: bool = False) -> ctk.CTkFrame:
    c = ctk.CTkFrame(parent, fg_color=Theme.BG_SECONDARY, corner_radius=Theme.RADIUS_LG, border_color=Theme.SECTION_BORDER, border_width=1)
    c.pack(fill="x", padx=CARD_PADX, pady=(0, pady_bottom))
    if accent_color:
        accent = ctk.CTkFrame(c, height=2, fg_color=accent_color, corner_radius=Theme.RADIUS_LG)
        accent.pack(fill="x", side="top", pady=0)
    if hover:
        def _on_enter(e):
            c.configure(border_color=accent_color if accent_color else Theme.ACCENT_PRIMARY)
        def _on_leave(e):
            c.configure(border_color=Theme.SECTION_BORDER)
        c.bind("<Enter>", _on_enter)
        c.bind("<Leave>", _on_leave)
    if title:
        ctk.CTkLabel(c, text=title.upper(), font=Theme.H3, text_color=title_color or Theme.BRAND_BLUE, anchor="w").pack(padx=INNER_PADX, pady=(SPACING_SM, SPACING_SM), anchor="w")
    return c

def card_spacer(parent):
    ctk.CTkFrame(parent, height=DIVIDER_HEIGHT, fg_color=Theme.SECTION_BORDER).pack(fill="x", padx=INNER_PADX, pady=SPACING_SM)

def info_banner(parent, title, text, color=Theme.ACCENT_PRIMARY):
    b = ctk.CTkFrame(parent, fg_color=Theme.BG_INPUT, corner_radius=Theme.RADIUS_MD, border_width=1, border_color=Theme.SECTION_BORDER)
    b.pack(fill="x", padx=CARD_PADX, pady=(0, SPACING_SM))
    ctk.CTkLabel(b, text=f"INFO: {title}", font=Theme.BODY_BOLD, text_color=color, anchor="w", justify="left").pack(padx=INNER_PADX, pady=(SPACING_SM, SPACING_XS), anchor="w", fill="x")
    ctk.CTkLabel(b, text=text, font=Theme.CAPTION, text_color=Theme.TEXT_DIM, justify="left", anchor="w", wraplength=600).pack(fill="x", padx=INNER_PADX, pady=(0, SPACING_SM))

def summary_row(parent: ctk.CTkFrame, row_idx: int, label: str, value_lbl_ref: str = None, sl_key: str = None, summary_labels: dict = None, status_key: str = None, edit_target: str = None, switch_fn: callable = None) -> ctk.CTkFrame:
    row = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=Theme.RADIUS_SM)
    row.grid(row=row_idx, column=0, sticky="ew", padx=INNER_PADX, pady=SPACING_XS)
    row.grid_columnconfigure(0, weight=1)
    if sl_key and summary_labels is not None:
        summary_labels[sl_key] = row
    row.bind("<Enter>", lambda e: row.configure(fg_color=Theme.BG_INPUT))
    row.bind("<Leave>", lambda e: row.configure(fg_color="transparent"))
    lbl = ctk.CTkLabel(row, text=label, font=Theme.BODY, text_color=Theme.TEXT_DIM, anchor="w", justify="left")
    lbl.grid(row=0, column=0, sticky="ew", padx=SPACING_SM, pady=SPACING_XS)
    col = 1
    if status_key and summary_labels is not None:
        dot = ctk.CTkLabel(row, text="●", font=Theme.ICON_SM, text_color=Theme.TEXT_DIM, anchor="center")
        dot.grid(row=0, column=col, sticky="center", padx=2)
        summary_labels[f"{status_key}_status"] = dot
        col += 1
    if edit_target and switch_fn:
        ctk.CTkButton(row, text="EDIT", width=ICON_BUTTON_WIDTH_SM, height=BUTTON_HEIGHT_SM, font=Theme.CAPTION, command=lambda: switch_fn(edit_target), **Theme.get_button_style("secondary")).grid(row=0, column=col, sticky="e", padx=SPACING_XS, pady=SPACING_XS)
        col += 1
    val = ctk.CTkLabel(row, text="₹ 0", font=Theme.DATA_BOLD, text_color=Theme.TEXT_PRIMARY, anchor="e")
    val.grid(row=0, column=col, sticky="e", padx=INNER_PADX, pady=SPACING_XS)
    if value_lbl_ref and summary_labels is not None:
        summary_labels[value_lbl_ref] = val
    return row
