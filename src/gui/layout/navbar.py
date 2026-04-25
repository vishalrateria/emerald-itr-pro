import customtkinter as ctk
from src.gui.styles.constants import (
    DROPDOWN_WIDTH_MD,
    ENTRY_HEIGHT,
    ICON_BUTTON_WIDTH_SM,
    NAVBAR_HEIGHT,
    SPACING_LG,
    SPACING_SM,
    SPACING_XS,
    NAVBAR_PADDING_X,
    NAVBAR_PADDING_Y,
    ACTION_BUTTON_WIDTH,
    ACTION_BUTTON_WIDTH_SM,
    DIVIDER_HEIGHT,
)
from src.gui.styles.theme import Theme
from src.gui.widgets.common import add_tooltip


class NavbarMixin:
    def _setup_navbar(self):
        self.navbar = ctk.CTkFrame(
            self,
            height=NAVBAR_HEIGHT,
            fg_color=Theme.BG_PRIMARY,
            corner_radius=0,
            border_width=0,
        )
        self.navbar.grid(row=0, column=0, sticky="ew")
        self.navbar.pack_propagate(False)
        self.navbar.grid_propagate(False)
        brand_frame = ctk.CTkFrame(self.navbar, fg_color="transparent")
        brand_frame.pack(side="left", padx=NAVBAR_PADDING_X, pady=NAVBAR_PADDING_Y)
        ctk.CTkLabel(
            brand_frame,
            text="EMERALD ITR PRO",
            font=Theme.H2,
            text_color=Theme.BRAND_BLUE,
            anchor="w",
        ).pack(side="left")
        ctk.CTkLabel(
            brand_frame,
            text=self.VERSION,
            font=Theme.CAPTION,
            text_color=Theme.TEXT_MUTED,
            anchor="w",
        ).pack(side="left", padx=(SPACING_SM, 0), pady=(2, 0))
        self.client_var = ctk.StringVar(value="No Client Selected")
        self.client_dropdown = ctk.CTkComboBox(
            self.navbar,
            variable=self.client_var,
            width=DROPDOWN_WIDTH_MD,
            height=ENTRY_HEIGHT,
            font=Theme.BODY,
            command=self.handle_client_dropdown_switch,
            **Theme.get_combo_style(),
        )
        self.client_dropdown.pack(side="left", padx=(SPACING_LG, SPACING_SM))
        ctk.CTkButton(
            self.navbar,
            text="+ NEW CLIENT",
            width=ACTION_BUTTON_WIDTH_SM,
            height=ENTRY_HEIGHT,
            font=Theme.BODY_BOLD,
            command=lambda: self.handle_add_client(self.client_master),
            **Theme.get_button_style("primary"),
        ).pack(side="left", padx=SPACING_SM)
        settings_btn = ctk.CTkButton(
            self.navbar,
            text="SETTINGS",
            width=ICON_BUTTON_WIDTH_SM,
            height=ENTRY_HEIGHT,
            font=Theme.CAPTION_BOLD,
            command=self.open_settings,
            **Theme.get_button_style("ghost"),
        )
        settings_btn.pack(
            side="right", padx=(SPACING_SM, NAVBAR_PADDING_X), pady=NAVBAR_PADDING_Y
        )
        add_tooltip(settings_btn, "Open Application Settings (Alt+S)")
        ctk.CTkFrame(
            self.navbar, width=DIVIDER_HEIGHT, fg_color=Theme.SECTION_BORDER
        ).pack(side="right", fill="y", pady=SPACING_XS)
        action_buttons = [
            ("CLEAR", self.clear_form, "danger", "Reset all form data (Ctrl+L)"),
            ("AI PANEL", self.show_ai_panel, "accent", "View AI suggestions panel"),
            (
                "AI AUDIT",
                self.run_ai_audit_diagnostic,
                "accent",
                "Run AI-powered tax audit and get suggestions",
            ),
            ("EXPORT", self.handle_export, "primary", "Export final ITR data to JSON"),
            (
                "PDF",
                self.handle_pdf_draft,
                "primary",
                "Generate draft PDF computation (Ctrl+P)",
            ),
            (
                "REPORT",
                self.handle_html_report,
                "secondary",
                "Generate full HTML computation report",
            ),
            (
                "CALENDAR",
                self.show_tax_calendar,
                "secondary",
                "View important tax deadlines",
            ),
            ("SYNC", self.show_sync_menu, "secondary", "Sync with Income Tax Portal"),
            (
                "BACKUP",
                self.show_backup_menu,
                "secondary",
                "Manage client database backups",
            ),
        ]
        for text, cmd, style, tt in action_buttons:
            btn = ctk.CTkButton(
                self.navbar,
                text=text,
                width=ACTION_BUTTON_WIDTH,
                height=ENTRY_HEIGHT,
                font=Theme.BODY_BOLD,
                command=cmd,
                **Theme.get_button_style(style),
            )
            btn.pack(side="right", padx=SPACING_SM, pady=SPACING_XS)
            add_tooltip(btn, tt)

    def update_client_dropdown(self):
        names = [
            f"{cd['name']} ({cid})" for cid, cd in self.client_master.clients.items()
        ]
        self.client_dropdown.configure(values=names)
        cid = self.client_master.current_client_id
        if cid in self.client_master.clients:
            self.client_var.set(f"{self.client_master.clients[cid]['name']} ({cid})")
