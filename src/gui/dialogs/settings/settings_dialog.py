import customtkinter as ctk
from tkinter import messagebox
from src.gui.styles.theme import Theme
from src.services.settings_service import SettingsManager
from src.gui.styles.constants import (
    BUTTON_HEIGHT,
    RADIUS_MD,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XS,
    MODAL_SECTION_HEIGHT,
    ACTION_BUTTON_WIDTH,
    ACTION_BUTTON_WIDTH_MD,
    ACTION_BUTTON_WIDTH_LG,
)
from src.config import APP_VERSION, AY_CYCLE

from .pages.general_page import build_page_general
from .pages.data_page import build_page_data
from .pages.pdf_page import build_page_pdf
from .pages.appearance_page import build_page_appearance
from .pages.advanced_page import build_page_advanced
from .pages.limits_page import build_page_limits
from .pages.about_page import build_page_about


class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_settings_saved=None):
        super().__init__(parent)
        self.on_settings_saved = on_settings_saved
        self._pages: dict[str, ctk.CTkFrame] = {}
        self._nav_btns: dict[str, ctk.CTkButton] = {}
        self._build_window()
        self._build_ui()
        self._load_values()
        self.after(10, self._center)
        self.grab_set()

    def register_var(self, key):
        return ctk.StringVar()

    def _build_window(self):
        self.title("⚙️  Settings  ·  Emerald ITR Pro")
        self._center_window(850, 620)
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_PRIMARY)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        Theme.apply_dark_title_bar(self)

    def _center_window(self, width: int, height: int):
        self.update_idletasks()
        try:
            px = self.master.winfo_rootx()
            py = self.master.winfo_rooty()
            pw = self.master.winfo_width()
            ph = self.master.winfo_height()
            x = px + (pw - width) // 2
            y = py + (ph - height) // 2
        except Exception:
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _center(self):
        pass

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color=Theme.BG_SECONDARY,
                               corner_radius=0, border_width=1,
                               border_color=Theme.SECTION_BORDER, height=MODAL_SECTION_HEIGHT)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="⚙️   Application Settings",
                     font=Theme.H2, text_color=Theme.BRAND_BLUE,
                     anchor="w").pack(side="left", padx=SPACING_LG, pady=SPACING_MD)
        ctk.CTkLabel(header, text=f"v{APP_VERSION}  ·  {AY_CYCLE}",
                     font=Theme.CAPTION, text_color=Theme.TEXT_MUTED,
                     anchor="e").pack(side="right", padx=SPACING_LG)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=0, minsize=180)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(body, fg_color=Theme.BG_SECONDARY,
                                corner_radius=0, border_width=0)
        sidebar.grid(row=0, column=0, sticky="nsew")

        self._content = ctk.CTkFrame(body, fg_color="transparent")
        self._content.grid(row=0, column=1, sticky="nsew", padx=SPACING_LG,
                           pady=SPACING_LG)
        self._content.grid_columnconfigure(0, weight=1)

        nav_items = [
            ("🗂️  General",    "general"),
            ("💾  Data & Backup", "data"),
            ("🖨️  PDF / Export", "pdf"),
            ("🎨  Appearance",  "appearance"),
            ("🛠️  Advanced",    "advanced"),
            ("🛡️  Limits",      "limits"),
            ("ℹ️  About",       "about"),
        ]
        ctk.CTkLabel(sidebar, text="SETTINGS",
                     font=Theme.CAPTION, text_color=Theme.TEXT_MUTED,
                     anchor="w").pack(fill="x", padx=SPACING_MD,
                                      pady=(SPACING_LG, SPACING_SM))
        for label, key in nav_items:
            btn = ctk.CTkButton(
                sidebar, text=label, font=Theme.BODY,
                fg_color="transparent", text_color=Theme.TEXT_DIM,
                anchor="w", hover_color=Theme.BG_INPUT,
                corner_radius=RADIUS_MD,
            )
            btn.pack(fill="x", padx=SPACING_SM, pady=SPACING_XS)
            btn.configure(command=lambda k=key: self._show_page(k))
            self._nav_btns[key] = btn

        build_page_general(self, self._make_page("general"))
        build_page_data(self, self._make_page("data"))
        build_page_pdf(self, self._make_page("pdf"))
        build_page_appearance(self, self._make_page("appearance"))
        build_page_advanced(self, self._make_page("advanced"))
        build_page_limits(self, self._make_page("limits"))
        build_page_about(self, self._make_page("about"))

        footer = ctk.CTkFrame(self, fg_color=Theme.BG_SECONDARY,
                               corner_radius=0, border_width=1,
                               border_color=Theme.SECTION_BORDER, height=MODAL_SECTION_HEIGHT)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        ctk.CTkButton(footer, text="✕  Cancel", width=ACTION_BUTTON_WIDTH,
                      height=BUTTON_HEIGHT, font=Theme.BODY_BOLD,
                      command=self.destroy,
                      **Theme.get_button_style("secondary")
                      ).pack(side="right", padx=SPACING_MD, pady=SPACING_SM)
        ctk.CTkButton(footer, text="💾  Save Settings", width=ACTION_BUTTON_WIDTH_MD,
                      height=BUTTON_HEIGHT, font=Theme.BODY_BOLD,
                      command=self._save,
                      **Theme.get_button_style("primary")
                      ).pack(side="right", padx=SPACING_SM, pady=SPACING_SM)
        ctk.CTkButton(footer, text="↺  Reset to Defaults", width=ACTION_BUTTON_WIDTH_LG,
                      height=BUTTON_HEIGHT, font=Theme.BODY_BOLD,
                      command=self._reset,
                      **Theme.get_button_style("danger")
                      ).pack(side="left", padx=SPACING_MD, pady=SPACING_SM)
        self._show_page("general")

    def _show_page(self, key: str):
        for k, frame in self._pages.items():
            frame.grid_remove()
        for k, btn in self._nav_btns.items():
            btn.configure(fg_color="transparent", text_color=Theme.TEXT_DIM,
                          font=Theme.BODY)
        if key in self._pages:
            self._pages[key].grid(row=0, column=0, sticky="nsew")
        if key in self._nav_btns:
            self._nav_btns[key].configure(
                fg_color=Theme.BG_INPUT, text_color=Theme.ACCENT_PRIMARY,
                font=Theme.BODY_BOLD)

    def _make_page(self, key: str) -> ctk.CTkScrollableFrame:
        f = ctk.CTkScrollableFrame(
            self._content, fg_color="transparent",
            scrollbar_button_color=Theme.SECTION_BORDER,
            scrollbar_button_hover_color=Theme.ACCENT_PRIMARY,
        )
        f.grid(row=0, column=0, sticky="nsew")
        f.grid_remove()
        self._pages[key] = f
        return f

    def _load_values(self):
        s = SettingsManager.load()
        as_map = {v: k for k, v in SettingsManager.get_autosave_options()}
        ms = s.get("autosave_interval_ms", 300000)
        label = as_map.get(ms, "5 minutes")
        self._v_autosave.set(label)
        self._v_default_itr.set(s.get("default_itr_type", "ITR-4"))
        self._v_open_last.set(bool(s.get("open_last_client_on_startup", True)))
        self._v_title_prefix.set(s.get("app_title_prefix", "EMERALD ITR PRO"))
        self._v_db_path.set(s.get("database_path", ""))
        self._v_backup_folder.set(s.get("backup_folder", ""))
        self._v_max_backups.set(str(s.get("max_rolling_backups", 5)))
        self._v_auto_backup.set(bool(s.get("auto_backup_enabled", True)))
        self._v_pdf_path.set(s.get("pdf_save_path", ""))
        self._v_ca_name.set(s.get("ca_name", ""))
        self._v_ca_reg.set(s.get("ca_reg_number", ""))
        self._v_firm_name.set(s.get("firm_name", ""))
        self._v_membership.set(s.get("membership_number", ""))
        self._v_font_scale.set(s.get("font_scale", "Normal"))
        self._v_tooltips.set(bool(s.get("show_shortcut_tooltips", True)))
        self._v_debounce.set(str(s.get("debounce_interval_ms", 300)))
        self._v_live_recompute.set(bool(s.get("enable_live_recompute", True)))
        self._v_log_level.set(s.get("log_level", "INFO"))
        self._v_max_bank.set(str(s.get("max_entries_bank", 5)))
        self._v_max_tds.set(str(s.get("max_entries_tds", 10)))
        self._v_max_tcs.set(str(s.get("max_entries_tcs", 10)))
        self._v_max_vda.set(str(s.get("max_entries_vda", 10)))
        self._v_max_biz.set(str(s.get("max_business_entities", 10)))
        self._v_max_hp.set(str(s.get("max_house_properties", 5)))
        self._v_max_cg.set(str(s.get("max_entries_cg", 10)))
        self._v_itr1_limit.set(str(s.get("itr1_gti_limit", 5000000)))
        self._v_ai_enabled.set(bool(s.get("ai_enabled", True)))

    def _save(self):
        as_map = {k: v for k, v in SettingsManager.get_autosave_options()}
        ms = as_map.get(self._v_autosave.get(), 300000)
        data = {
            "autosave_interval_ms": ms,
            "default_itr_type": self._v_default_itr.get(),
            "open_last_client_on_startup": self._v_open_last.get(),
            "app_title_prefix": self._v_title_prefix.get() or "EMERALD ITR PRO",
            "database_path": self._v_db_path.get(),
            "backup_folder": self._v_backup_folder.get(),
            "max_rolling_backups": 5,
            "auto_backup_enabled": self._v_auto_backup.get(),
        }
        try:
            data["max_rolling_backups"] = int(self._v_max_backups.get() or 5)
        except (ValueError, TypeError):
            pass
        data.update({
            "pdf_save_path": self._v_pdf_path.get(),
            "ca_name": self._v_ca_name.get(),
            "ca_reg_number": self._v_ca_reg.get(),
            "firm_name": self._v_firm_name.get(),
            "membership_number": self._v_membership.get(),
            "font_scale": self._v_font_scale.get(),
            "show_shortcut_tooltips": self._v_tooltips.get(),
            "theme_mode": "dark",
            "debounce_interval_ms": int(self._v_debounce.get() or 300),
            "enable_live_recompute": self._v_live_recompute.get(),
            "log_level": self._v_log_level.get(),
            "max_entries_bank": int(self._v_max_bank.get() or 5),
            "max_entries_tds": int(self._v_max_tds.get() or 10),
            "max_entries_tcs": int(self._v_max_tcs.get() or 10),
            "max_entries_vda": int(self._v_max_vda.get() or 10),
            "max_business_entities": int(self._v_max_biz.get() or 10),
            "max_house_properties": int(self._v_max_hp.get() or 5),
            "max_entries_cg": int(self._v_max_cg.get() or 10),
            "itr1_gti_limit": int(self._v_itr1_limit.get() or 5000000),
            "ai_enabled": self._v_ai_enabled.get(),
        })
        if SettingsManager.save(data):
            if self.on_settings_saved:
                self.on_settings_saved(data)
            messagebox.showinfo("Settings Saved",
                                "Settings saved. Theme changes applied to main UI.\nRestart app for full theme effect on all components.",
                                parent=self)
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to save settings.", parent=self)

    def _reset(self):
        if messagebox.askyesno("Reset Settings",
                               "Reset ALL settings to defaults?\nThis cannot be undone.",
                               parent=self):
            SettingsManager.reset_to_defaults()
            self._load_values()
            messagebox.showinfo("Reset", "Settings reset to defaults.", parent=self)
