import customtkinter as ctk
from src.gui.styles.constants import (
    BUTTON_HEIGHT, BUTTON_HEIGHT_MD, NAV_SIDEBAR_WIDTH, RADIUS_SM,
    SIDEBAR_BUTTON_HEIGHT, ACTION_BUTTON_WIDTH_MD, ACTION_BUTTON_WIDTH_LG,
    SPACING_LG, SPACING_MD, SPACING_SM, SPACING_XS,
    FOOTER_PADDING_X, FOOTER_PADDING_Y,
)
from src.gui.styles.theme import Theme
from src.gui.dialogs.client_master_view import ClientMaster
from src.services.logging_service import log as logger


class MainLayoutMixin:
    def setup_layout(self):
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self._setup_navbar()
        self._setup_summary_bar()
        self._setup_main_content()
        self._setup_status_bar()
        logger.info("🎨 UI Layout initialized")
        self.client_master = ClientMaster(self, self.handle_client_switch, self.handle_save_and_switch)
        self.init_frames()

    def _setup_main_content(self):
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=2, column=0, sticky="nsew", padx=0, pady=0)
        self.main_container.grid_columnconfigure(0, weight=0, minsize=NAV_SIDEBAR_WIDTH)
        self.main_container.grid_columnconfigure(1, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.sidebar = ctk.CTkFrame(self.main_container, fg_color=Theme.BG_RECESSED, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.sidebar, text="FILING STEPS", font=Theme.CAPTION_BOLD, text_color=Theme.TEXT_MUTED, anchor="w", justify="left").pack(fill="x", padx=SPACING_MD, pady=(SPACING_LG, SPACING_XS))
        self.steps = [
            {"id": "setup", "title": "Profile Setup", "frames": ["profile_config"]},
            {"id": "personal", "title": "Personal Info", "frames": ["personal"]},
            {"id": "income_salary", "title": "Salary Income", "frames": ["salary"]},
            {"id": "income_hp", "title": "House Property", "frames": ["hp"]},
            {"id": "income_bp", "title": "Business & Profession", "frames": ["business_financials", "44ad", "44ada", "44ae", "tb", "bs"]},
            {"id": "income_cg", "title": "Capital Gains", "frames": ["stcg", "ltcg", "vda"]},
            {"id": "income_os", "title": "Other Sources", "frames": ["other_sources"]},
            {"id": "foreign_assets", "title": "Foreign Assets", "frames": ["fa"]},
            {"id": "deductions", "title": "Deductions", "frames": ["deductions", "exempt"]},
            {"id": "taxes", "title": "Taxes Paid", "frames": ["tax"]},
            {"id": "review", "title": "Computation Dashboard", "frames": ["master"]},
            {"id": "verify", "title": "Verification", "frames": ["verify"]},
            {"id": "tools", "title": "Audit Tools", "frames": ["wizard", "audit_workspace"]},
        ]
        self.current_step_idx = 0
        self.step_buttons = {}
        self.steps_container = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent", corner_radius=0, scrollbar_button_color=Theme.BG_RECESSED)
        self.steps_container.pack(fill="both", expand=True)
        
        for idx, step in enumerate(self.steps):
            row = ctk.CTkFrame(self.steps_container, fg_color="transparent", height=SIDEBAR_BUTTON_HEIGHT)
            row.pack(fill="x", side="top", pady=1)
            row.pack_propagate(False)
            
            indicator = ctk.CTkFrame(row, width=4, fg_color="transparent", corner_radius=2)
            indicator.pack(side="left", fill="y", padx=(2, 0))
            
            display_text = f"  {idx+1}.  {step['title']}"
            btn = ctk.CTkButton(row, text=display_text, font=Theme.BODY_BOLD, height=SIDEBAR_BUTTON_HEIGHT, fg_color="transparent", text_color=Theme.TEXT_MUTED, anchor="w", hover_color=Theme.BG_HOVER, corner_radius=RADIUS_SM, command=lambda i=idx: self.go_to_step(i))
            btn.pack(side="left", fill="both", expand=True, padx=(2, SPACING_SM))
            
            self.step_buttons[idx] = (btn, indicator, row)
        self.content_area = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(1, weight=0)
        self.scrollable_content = ctk.CTkScrollableFrame(self.content_area, fg_color="transparent", scrollbar_button_color=Theme.SECTION_BORDER, scrollbar_button_hover_color=Theme.ACCENT_PRIMARY)
        self.scrollable_content.grid(row=0, column=0, sticky="nsew")
        self.footer = ctk.CTkFrame(self.content_area, height=BUTTON_HEIGHT * 2, fg_color=Theme.BG_SECONDARY, corner_radius=0, border_width=1, border_color=Theme.SECTION_BORDER)
        self.footer.grid(row=1, column=0, sticky="ew")
        footer_btn_container = ctk.CTkFrame(self.footer, fg_color="transparent")
        footer_btn_container.pack(fill="x", padx=FOOTER_PADDING_X, pady=FOOTER_PADDING_Y)
        self.btn_prev = ctk.CTkButton(footer_btn_container, text="← Previous", command=self.prev_step, height=BUTTON_HEIGHT, width=ACTION_BUTTON_WIDTH_MD, font=Theme.BODY_BOLD, **Theme.get_button_style("secondary"))
        self.btn_prev.pack(side="left", padx=SPACING_SM)
        self.btn_next = ctk.CTkButton(footer_btn_container, text="Save & Continue →", command=self.next_step, height=BUTTON_HEIGHT, width=ACTION_BUTTON_WIDTH_LG, font=Theme.BODY_BOLD, **Theme.get_button_style("primary"))
        self.btn_next.pack(side="right", padx=SPACING_SM)
