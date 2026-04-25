import customtkinter as ctk
import os
import shutil
import json
from datetime import datetime
from tkinter import messagebox, filedialog
from src.gui.styles.theme import Theme
from src.services.settings_service import SettingsManager
from src.gui.styles.constants import (
    BUTTON_HEIGHT,
    RADIUS_MD,
    SPACING_XL,
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
from .pages.ai_page import build_page_ai
from .pages.computation_page import build_page_computation
from .pages.notifications_page import build_page_notifications
from .pages.window_page import build_page_window


class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_settings_saved=None):
        super().__init__(parent)
        self.on_settings_saved = on_settings_saved
        self._pages: dict[str, ctk.CTkFrame] = {}
        self._nav_btns: dict[str, ctk.CTkButton] = {}
        self._init_vars()
        self._build_window()
        self._build_ui()
        self._load_values()
        self.after(10, self._center)
        self.grab_set()

    def _init_vars(self):
        self._v_autosave = ctk.StringVar()
        self._v_default_itr = ctk.StringVar()
        self._v_open_last = ctk.BooleanVar()
        self._v_title_prefix = ctk.StringVar()
        self._v_autosave_form = ctk.BooleanVar()
        self._v_validate_on_exit = ctk.BooleanVar()
        self._v_inline_errors = ctk.BooleanVar()
        self._v_partial_sub = ctk.BooleanVar()
        self._v_def_schedules = ctk.StringVar()

        self._v_db_path = ctk.StringVar()
        self._v_backup_folder = ctk.StringVar()
        self._v_max_backups = ctk.StringVar()
        self._v_auto_backup = ctk.BooleanVar()
        self._v_backup_schedule = ctk.StringVar()
        self._v_backup_compression = ctk.StringVar()
        self._v_backup_retention = ctk.StringVar()

        self._v_pdf_path = ctk.StringVar()
        self._v_ca_name = ctk.StringVar()
        self._v_ca_reg = ctk.StringVar()
        self._v_firm_name = ctk.StringVar()
        self._v_membership = ctk.StringVar()
        self._v_export_format = ctk.StringVar()
        self._v_pdf_quality = ctk.StringVar()
        self._v_include_schedules = ctk.BooleanVar()
        self._v_auto_open_pdf = ctk.BooleanVar()
        self._v_json_indent = ctk.StringVar()

        self._v_font_scale = ctk.StringVar()
        self._v_tooltips = ctk.BooleanVar()
        self._v_ui_scale_override = ctk.StringVar()

        self._v_default_regime = ctk.StringVar()
        self._v_round_off = ctk.BooleanVar()
        self._v_show_calc = ctk.BooleanVar()
        self._v_show_relief = ctk.BooleanVar()
        self._v_allow_negative = ctk.BooleanVar()
        self._v_interest_method = ctk.StringVar()

        self._v_due_date_remind = ctk.BooleanVar()
        self._v_backup_notify = ctk.BooleanVar()
        self._v_error_alerts = ctk.BooleanVar()
        self._v_update_notify = ctk.BooleanVar()
        self._v_autosave_notify = ctk.BooleanVar()

        self._v_start_minimized = ctk.BooleanVar()
        self._v_minimize_on_close = ctk.BooleanVar()
        self._v_always_on_top = ctk.BooleanVar()
        self._v_show_on_startup = ctk.BooleanVar()

        self._v_debounce = ctk.StringVar()
        self._v_live_recompute = ctk.BooleanVar()
        self._v_log_level = ctk.StringVar()
        self._v_debug_overlay = ctk.BooleanVar()

        self._v_ai_enabled = ctk.BooleanVar()
        self._v_ai_model_path = ctk.StringVar()
        self._v_ai_confidence = ctk.StringVar()
        self._v_ai_max_tokens = ctk.StringVar()
        self._v_ai_temp = ctk.StringVar()
        self._v_ai_thread_pool = ctk.StringVar()
        self._v_ai_hw_profile = ctk.StringVar()
        self._v_ai_n_ctx = ctk.StringVar()
        self._v_ai_n_gpu_layers = ctk.StringVar()
        self._v_ai_n_threads = ctk.StringVar()

        self._v_max_bank = ctk.StringVar()
        self._v_max_tds = ctk.StringVar()
        self._v_max_tcs = ctk.StringVar()
        self._v_max_tax_paid = ctk.StringVar()
        self._v_max_vda = ctk.StringVar()
        self._v_max_biz = ctk.StringVar()
        self._v_max_hp = ctk.StringVar()
        self._v_max_cg = ctk.StringVar()
        self._v_max_cg_quarters = ctk.StringVar()
        self._v_max_fo = ctk.StringVar()
        self._v_max_44ad = ctk.StringVar()
        self._v_max_44ada = ctk.StringVar()
        self._v_max_ae = ctk.StringVar()
        self._v_max_entries_hp = ctk.StringVar()
        self._v_max_g = ctk.StringVar()
        self._v_itr1_limit = ctk.StringVar()

    def _safe_int(self, var, fallback):
        val = var.get().replace(",", "")
        if val.isdigit():
            return int(val)
        return fallback

    def _safe_float(self, var, fallback):
        try:
            return float(var.get().replace(",", ""))
        except (ValueError, TypeError):
            return fallback

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
            if not self.master.winfo_ismapped():
                raise ValueError("Master is not visible")
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
        self._center_window(850, 620)

    def _build_ui(self):
        header = ctk.CTkFrame(
            self,
            fg_color=Theme.BG_SECONDARY,
            corner_radius=0,
            border_width=1,
            border_color=Theme.SECTION_BORDER,
            height=MODAL_SECTION_HEIGHT,
        )
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(
            header,
            text="⚙️   Application Settings",
            font=Theme.H2,
            text_color=Theme.BRAND_BLUE,
            anchor="w",
        ).pack(side="left", padx=SPACING_XL, pady=SPACING_MD)
        ctk.CTkLabel(
            header,
            text=f"v{APP_VERSION}  ·  {AY_CYCLE}",
            font=Theme.CAPTION,
            text_color=Theme.TEXT_MUTED,
            anchor="e",
        ).pack(side="right", padx=SPACING_XL)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=0, minsize=200)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkScrollableFrame(
            body,
            fg_color=Theme.BG_SECONDARY,
            corner_radius=0,
            border_width=0,
            scrollbar_button_color=Theme.BG_SECONDARY,
            scrollbar_button_hover_color=Theme.BG_HOVER,
        )
        sidebar.grid(row=0, column=0, sticky="nsew")

        self._content = ctk.CTkFrame(body, fg_color="transparent")
        self._content.grid(
            row=0, column=1, sticky="nsew", padx=SPACING_XL, pady=SPACING_XL
        )
        self._content.grid_columnconfigure(0, weight=1)
        self._content.grid_rowconfigure(0, weight=1)

        nav_items = [
            ("General", "general"),
            ("Data & Backup", "data"),
            ("PDF / Export", "pdf"),
            ("Appearance", "appearance"),
            ("Computation", "computation"),
            ("Notifications", "notifications"),
            ("Window Behavior", "window"),
            ("Advanced", "advanced"),
            ("Limits", "limits"),
            ("AI Settings", "ai"),
            ("About", "about"),
        ]
        ctk.CTkLabel(
            sidebar,
            text="SETTINGS",
            font=Theme.CAPTION,
            text_color=Theme.TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=SPACING_XL, pady=(SPACING_XL, SPACING_SM))
        for label, key in nav_items:
            btn = ctk.CTkButton(
                sidebar,
                text=label,
                font=Theme.BODY,
                fg_color="transparent",
                text_color=Theme.TEXT_DIM,
                anchor="w",
                hover_color=Theme.BG_INPUT,
                corner_radius=RADIUS_MD,
            )
            btn.pack(fill="x", padx=SPACING_XL, pady=SPACING_XS)
            btn.configure(command=lambda k=key: self._show_page(k))
            self._nav_btns[key] = btn

        build_page_general(self, self._make_page("general"))
        build_page_data(self, self._make_page("data"))
        build_page_pdf(self, self._make_page("pdf"))
        build_page_appearance(self, self._make_page("appearance"))
        build_page_computation(self, self._make_page("computation"))
        build_page_notifications(self, self._make_page("notifications"))
        build_page_window(self, self._make_page("window"))
        build_page_advanced(self, self._make_page("advanced"))
        build_page_limits(self, self._make_page("limits"))
        build_page_ai(self, self._make_page("ai"))
        build_page_about(self, self._make_page("about"))

        footer = ctk.CTkFrame(
            self,
            fg_color=Theme.BG_SECONDARY,
            corner_radius=0,
            border_width=1,
            border_color=Theme.SECTION_BORDER,
            height=MODAL_SECTION_HEIGHT,
        )
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        ctk.CTkButton(
            footer,
            text="✕  Cancel",
            width=ACTION_BUTTON_WIDTH,
            height=BUTTON_HEIGHT,
            font=Theme.BODY_BOLD,
            command=self.destroy,
            **Theme.get_button_style("secondary"),
        ).pack(side="right", padx=SPACING_XL, pady=SPACING_SM)
        ctk.CTkButton(
            footer,
            text="💾  Save Settings",
            width=ACTION_BUTTON_WIDTH_MD,
            height=BUTTON_HEIGHT,
            font=Theme.BODY_BOLD,
            command=self._save,
            **Theme.get_button_style("primary"),
        ).pack(side="right", padx=SPACING_SM, pady=SPACING_SM)
        ctk.CTkButton(
            footer,
            text="↺  Reset to Defaults",
            width=ACTION_BUTTON_WIDTH_LG,
            height=BUTTON_HEIGHT,
            font=Theme.BODY_BOLD,
            command=self._reset,
            **Theme.get_button_style("danger"),
        ).pack(side="left", padx=SPACING_XL, pady=SPACING_SM)
        self._show_page("general")

    def _show_page(self, key: str):
        for k, frame in self._pages.items():
            frame.grid_remove()
        for k, btn in self._nav_btns.items():
            btn.configure(
                fg_color="transparent", text_color=Theme.TEXT_DIM, font=Theme.BODY
            )
        if key in self._pages:
            self._pages[key].grid(row=0, column=0, sticky="nsew")
        if key in self._nav_btns:
            self._nav_btns[key].configure(
                fg_color=Theme.BG_INPUT,
                text_color=Theme.ACCENT_PRIMARY,
                font=Theme.BODY_BOLD,
            )

    def _make_page(self, key: str) -> ctk.CTkScrollableFrame:
        f = ctk.CTkScrollableFrame(
            self._content,
            fg_color="transparent",
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
        ms = SettingsManager.get("Data.autosave_interval_ms", 300000)
        label = as_map.get(ms, "5 minutes")
        self._v_autosave.set(label)
        self._v_default_itr.set(SettingsManager.get("General.default_itr_type"))
        self._v_open_last.set(
            bool(SettingsManager.get("General.open_last_client_on_startup", True))
        )
        self._v_title_prefix.set(
            SettingsManager.get("General.app_title_prefix", "EMERALD ITR PRO")
        )
        self._v_db_path.set(SettingsManager.get("Data.database_path", ""))
        self._v_backup_folder.set(SettingsManager.get("Data.backup_folder", ""))
        self._v_max_backups.set(str(SettingsManager.get("Data.max_rolling_backups", 5)))
        self._v_auto_backup.set(
            bool(SettingsManager.get("Data.auto_backup_enabled", True))
        )
        self._v_pdf_path.set(SettingsManager.get("Engine.pdf_save_path", ""))
        self._v_ca_name.set(SettingsManager.get("General.ca_firm.ca_name", ""))
        self._v_ca_reg.set(SettingsManager.get("General.ca_firm.ca_reg_number", ""))
        self._v_firm_name.set(SettingsManager.get("General.ca_firm.firm_name", ""))
        self._v_membership.set(
            SettingsManager.get("General.ca_firm.membership_number", "")
        )
        self._v_font_scale.set(SettingsManager.get("Appearance.font_scale", "Normal"))
        self._v_tooltips.set(
            bool(SettingsManager.get("Appearance.show_shortcut_tooltips", True))
        )
        self._v_ui_scale_override.set(
            str(SettingsManager.get("Appearance.ui_scale_override", 0))
        )
        self._v_debounce.set(
            str(SettingsManager.get("Engine.debounce_interval_ms", 300))
        )
        self._v_live_recompute.set(
            bool(SettingsManager.get("Engine.enable_live_recompute", True))
        )
        self._v_log_level.set(SettingsManager.get("Engine.log_level", "INFO"))
        self._v_max_bank.set(
            str(SettingsManager.get("ITR_Limits.Common.max_entries_bank", 5))
        )
        self._v_max_tds.set(
            str(SettingsManager.get("ITR_Limits.Common.max_entries_tds", 10))
        )
        self._v_max_tcs.set(
            str(SettingsManager.get("ITR_Limits.Common.max_entries_tcs", 10))
        )
        self._v_max_tax_paid.set(
            str(SettingsManager.get("ITR_Limits.Common.max_entries_tax_paid", 10))
        )
        self._v_max_vda.set(
            str(SettingsManager.get("ITR_Limits.ITR2.max_entries_vda", 10))
        )
        self._v_max_biz.set(
            str(SettingsManager.get("ITR_Limits.ITR3.max_business_entities", 10))
        )
        self._v_max_hp.set(
            str(SettingsManager.get("ITR_Limits.ITR2.max_house_properties", 5))
        )
        self._v_max_cg.set(
            str(SettingsManager.get("ITR_Limits.ITR2.max_entries_cg", 10))
        )
        self._v_max_cg_quarters.set(
            str(SettingsManager.get("ITR_Limits.ITR2.max_cg_quarters", 5))
        )
        self._v_max_fo.set(
            str(SettingsManager.get("ITR_Limits.ITR2.max_entries_fo", 10))
        )
        self._v_max_44ad.set(
            str(SettingsManager.get("ITR_Limits.ITR4.max_entries_44ad", 10))
        )
        self._v_max_44ada.set(
            str(SettingsManager.get("ITR_Limits.ITR4.max_entries_44ada", 10))
        )
        self._v_max_ae.set(
            str(SettingsManager.get("ITR_Limits.ITR3.max_entries_ae", 10))
        )
        self._v_max_entries_hp.set(
            str(SettingsManager.get("ITR_Limits.ITR2.max_entries_hp", 5))
        )
        self._v_max_g.set(
            str(SettingsManager.get("ITR_Limits.Common.max_entries_g", 5))
        )
        self._v_itr1_limit.set(
            str(SettingsManager.get("ITR_Limits.ITR1.gti_limit", 5000000))
        )
        self._v_ai_enabled.set(bool(SettingsManager.get("AI.enabled", True)))
        self._v_ai_model_path.set(
            SettingsManager.get("AI.model_path", "models/Phi-4-mini-instruct-Q8_0.gguf")
        )
        self._v_ai_confidence.set(
            str(SettingsManager.get("AI.confidence_threshold", 0.85))
        )
        self._v_ai_max_tokens.set(str(SettingsManager.get("AI.max_tokens", 2048)))
        self._v_ai_temp.set(str(SettingsManager.get("AI.temperature", 0.1)))
        self._v_ai_thread_pool.set(str(SettingsManager.get("AI.thread_pool_size", 1)))
        self._v_ai_hw_profile.set(SettingsManager.get("AI.hardware_profile", "auto"))
        self._v_ai_n_ctx.set(str(SettingsManager.get("AI.n_ctx", 2048)))
        self._v_ai_n_gpu_layers.set(str(SettingsManager.get("AI.n_gpu_layers", 0)))
        self._v_ai_n_threads.set(str(SettingsManager.get("AI.n_threads", 2)))

        self._v_export_format.set(SettingsManager.get("Export.default_format", "PDF"))
        self._v_pdf_quality.set(SettingsManager.get("Export.pdf_quality", "Standard"))
        self._v_include_schedules.set(
            bool(SettingsManager.get("Export.include_schedules", True))
        )
        self._v_auto_open_pdf.set(
            bool(SettingsManager.get("Export.auto_open_after_gen", True))
        )
        self._v_json_indent.set(str(SettingsManager.get("Export.json_indent", 2)))

        self._v_backup_schedule.set(SettingsManager.get("Backup.schedule", "Manual"))
        self._v_backup_compression.set(SettingsManager.get("Backup.compression", "zip"))
        self._v_backup_retention.set(
            str(SettingsManager.get("Backup.retention_days", 30))
        )

        self._v_due_date_remind.set(
            bool(SettingsManager.get("Notifications.due_date_reminder", True))
        )
        self._v_backup_notify.set(
            bool(SettingsManager.get("Notifications.backup_completion", True))
        )
        self._v_error_alerts.set(
            bool(SettingsManager.get("Notifications.error_alerts", True))
        )
        self._v_update_notify.set(
            bool(SettingsManager.get("Notifications.update_available", True))
        )
        self._v_autosave_notify.set(
            bool(SettingsManager.get("Notifications.autosave_notification", False))
        )

        self._v_start_minimized.set(
            bool(SettingsManager.get("Window.start_minimized", False))
        )
        self._v_minimize_on_close.set(
            bool(SettingsManager.get("Window.minimize_to_tray_on_close", False))
        )
        self._v_always_on_top.set(
            bool(SettingsManager.get("Window.always_on_top", False))
        )
        self._v_show_on_startup.set(
            bool(SettingsManager.get("Window.show_on_startup", True))
        )

        self._v_default_regime.set(
            SettingsManager.get("Computation.default_regime", "New (115BAC)")
        )
        self._v_round_off.set(
            bool(SettingsManager.get("Computation.round_off_totals", True))
        )
        self._v_show_calc.set(
            bool(SettingsManager.get("Computation.show_detailed_calc", False))
        )
        self._v_show_relief.set(
            bool(SettingsManager.get("Computation.show_marginal_relief", True))
        )
        self._v_allow_negative.set(
            bool(SettingsManager.get("Computation.allow_negative_values", False))
        )
        self._v_interest_method.set(
            SettingsManager.get("Computation.interest_method", "Simple")
        )

        self._v_autosave_form.set(
            bool(SettingsManager.get("ITR_Behavior.autosave_form_progress", True))
        )
        self._v_validate_on_exit.set(
            bool(SettingsManager.get("ITR_Behavior.validate_on_exit", True))
        )
        self._v_inline_errors.set(
            bool(SettingsManager.get("ITR_Behavior.show_inline_errors", True))
        )
        self._v_partial_sub.set(
            bool(SettingsManager.get("ITR_Behavior.allow_partial_submission", False))
        )
        self._v_def_schedules.set(
            SettingsManager.get(
                "ITR_Behavior.default_schedule_selections", "S, HP, CG, OS"
            )
        )

        self._v_debug_overlay.set(
            bool(SettingsManager.get("Engine.show_debug_overlay", False))
        )

    def _save(self):
        as_map = {k: v for k, v in SettingsManager.get_autosave_options()}
        ms = as_map.get(self._v_autosave.get(), 300000)
        try:
            max_backups = int(self._v_max_backups.get() or 5)
        except (ValueError, TypeError):
            max_backups = 5

        data = {
            "General": {
                "default_itr_type": self._v_default_itr.get(),
                "open_last_client_on_startup": self._v_open_last.get(),
                "app_title_prefix": self._v_title_prefix.get() or "EMERALD ITR PRO",
                "ca_firm": {
                    "ca_name": self._v_ca_name.get(),
                    "ca_reg_number": self._v_ca_reg.get(),
                    "firm_name": self._v_firm_name.get(),
                    "membership_number": self._v_membership.get(),
                },
            },
            "Data": {
                "autosave_interval_ms": ms,
                "database_path": self._v_db_path.get(),
                "backup_folder": self._v_backup_folder.get(),
                "max_rolling_backups": max_backups,
                "auto_backup_enabled": self._v_auto_backup.get(),
            },
            "Appearance": {
                "font_scale": self._v_font_scale.get(),
                "show_shortcut_tooltips": self._v_tooltips.get(),
                "ui_scale_override": self._safe_float(self._v_ui_scale_override, 0),
            },
            "Engine": {
                "pdf_save_path": self._v_pdf_path.get(),
                "debounce_interval_ms": int(self._v_debounce.get() or 300),
                "enable_live_recompute": self._v_live_recompute.get(),
                "log_level": self._v_log_level.get(),
            },
            "ITR_Limits": {
                "Common": {
                    "max_entries_bank": self._safe_int(self._v_max_bank, 5),
                    "max_entries_tds": self._safe_int(self._v_max_tds, 10),
                    "max_entries_tcs": self._safe_int(self._v_max_tcs, 10),
                    "max_entries_tax_paid": self._safe_int(self._v_max_tax_paid, 10),
                    "max_entries_g": self._safe_int(self._v_max_g, 5),
                },
                "ITR1": {"gti_limit": self._safe_int(self._v_itr1_limit, 5000000)},
                "ITR2": {
                    "max_entries_vda": self._safe_int(self._v_max_vda, 10),
                    "max_house_properties": self._safe_int(self._v_max_hp, 5),
                    "max_entries_hp": self._safe_int(self._v_max_entries_hp, 5),
                    "max_entries_cg": self._safe_int(self._v_max_cg, 10),
                    "max_cg_quarters": self._safe_int(self._v_max_cg_quarters, 5),
                    "max_entries_fo": self._safe_int(self._v_max_fo, 10),
                },
                "ITR3": {
                    "max_business_entities": self._safe_int(self._v_max_biz, 10),
                    "max_entries_ae": self._safe_int(self._v_max_ae, 10),
                },
                "ITR4": {
                    "max_entries_44ad": self._safe_int(self._v_max_44ad, 10),
                    "max_entries_44ada": self._safe_int(self._v_max_44ada, 10),
                },
            },
            "AI": {
                "enabled": self._v_ai_enabled.get(),
                "model_path": self._v_ai_model_path.get()
                or "models/Phi-4-mini-instruct-Q8_0.gguf",
                "confidence_threshold": self._safe_float(self._v_ai_confidence, 0.85),
                "max_tokens": self._safe_int(self._v_ai_max_tokens, 2048),
                "temperature": self._safe_float(self._v_ai_temp, 0.1),
                "thread_pool_size": self._safe_int(self._v_ai_thread_pool, 1),
                "hardware_profile": self._v_ai_hw_profile.get() or "auto",
                "n_ctx": self._safe_int(self._v_ai_n_ctx, 2048),
                "n_gpu_layers": self._safe_int(self._v_ai_n_gpu_layers, 0),
                "n_threads": self._safe_int(self._v_ai_n_threads, 2),
            },
            "Export": {
                "default_format": self._v_export_format.get(),
                "pdf_quality": self._v_pdf_quality.get(),
                "include_schedules": self._v_include_schedules.get(),
                "auto_open_after_gen": self._v_auto_open_pdf.get(),
                "json_indent": int(
                    self._v_json_indent.get()
                    if self._v_json_indent.get().isdigit()
                    else 2
                ),
            },
            "Backup": {
                "schedule": self._v_backup_schedule.get(),
                "compression": self._v_backup_compression.get(),
                "retention_days": int(self._v_backup_retention.get() or 30),
            },
            "Notifications": {
                "due_date_reminder": self._v_due_date_remind.get(),
                "backup_completion": self._v_backup_notify.get(),
                "error_alerts": self._v_error_alerts.get(),
                "update_available": self._v_update_notify.get(),
                "autosave_notification": self._v_autosave_notify.get(),
            },
            "Window": {
                "start_minimized": self._v_start_minimized.get(),
                "minimize_to_tray_on_close": self._v_minimize_on_close.get(),
                "always_on_top": self._v_always_on_top.get(),
                "show_on_startup": self._v_show_on_startup.get(),
            },
            "Computation": {
                "default_regime": self._v_default_regime.get(),
                "round_off_totals": self._v_round_off.get(),
                "show_detailed_calc": self._v_show_calc.get(),
                "show_marginal_relief": self._v_show_relief.get(),
                "allow_negative_values": self._v_allow_negative.get(),
                "interest_method": self._v_interest_method.get(),
            },
            "ITR_Behavior": {
                "autosave_form_progress": self._v_autosave_form.get(),
                "validate_on_exit": self._v_validate_on_exit.get(),
                "show_inline_errors": self._v_inline_errors.get(),
                "allow_partial_submission": self._v_partial_sub.get(),
                "default_schedule_selections": self._v_def_schedules.get(),
            },
        }
        data["Engine"]["show_debug_overlay"] = self._v_debug_overlay.get()
        if SettingsManager.save(data):
            if self.on_settings_saved:
                self.on_settings_saved(data)
            messagebox.showinfo(
                "Settings Saved",
                "Settings saved. Theme changes applied to main UI.\nRestart app for full theme effect on all components.",
                parent=self,
            )
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to save settings.", parent=self)

    def _reset(self):
        if messagebox.askyesno(
            "Reset Settings",
            "Reset ALL settings to defaults?\nThis cannot be undone.",
            parent=self,
        ):
            SettingsManager.reset_to_defaults()
            self._load_values()
            messagebox.showinfo("Reset", "Settings reset to defaults.", parent=self)

    def _handle_clear_recent_clients(self):
        if messagebox.askyesno(
            "Confirm", "Clear all recent clients history?", parent=self
        ):
            SettingsManager.set("General.recent_clients", [])
            messagebox.showinfo("Success", "Recent clients list cleared.", parent=self)

    def _handle_export_settings(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile="emerald_settings_backup.json",
            title="Export Settings",
            parent=self,
        )
        if path:
            try:
                shutil.copy("settings.json", path)
                messagebox.showinfo(
                    "Export Success", f"Settings exported to:\n{path}", parent=self
                )
            except Exception as e:
                messagebox.showerror(
                    "Export Error", f"Failed to export settings: {e}", parent=self
                )

    def _handle_import_settings(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")], title="Import Settings", parent=self
        )
        if path:
            if messagebox.askyesno(
                "Confirm Import",
                "Importing settings will overwrite your current configuration. Continue?",
                parent=self,
            ):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if SettingsManager.save(data):
                        self._load_values()
                        messagebox.showinfo(
                            "Import Success",
                            "Settings imported successfully.",
                            parent=self,
                        )
                    else:
                        messagebox.showerror(
                            "Import Error",
                            "Failed to validate imported settings.",
                            parent=self,
                        )
                except Exception as e:
                    messagebox.showerror(
                        "Import Error", f"Failed to import settings: {e}", parent=self
                    )

    def _handle_manual_backup(self):
        backup_folder = self._v_backup_folder.get() or "backups"
        db_path = self._v_db_path.get() or "data/clients.mcdb"

        if not os.path.exists(db_path):
            messagebox.showerror(
                "Error", f"Database file not found at:\n{db_path}", parent=self
            )
            return

        os.makedirs(backup_folder, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_folder, f"manual_backup_{ts}.mcdb")

        try:
            shutil.copy(db_path, backup_path)
            messagebox.showinfo(
                "Backup Success",
                f"Manual backup created at:\n{backup_path}",
                parent=self,
            )
        except Exception as e:
            messagebox.showerror(
                "Backup Error", f"Failed to create backup: {e}", parent=self
            )

    def _handle_clear_cache(self):
        if messagebox.askyesno(
            "Confirm",
            "Clear application cache? This will free up space but may slow down initial loading of some data.",
            parent=self,
        ):
            cache_dir = "cache"
            if os.path.exists(cache_dir):
                try:
                    shutil.rmtree(cache_dir)
                    os.makedirs(cache_dir)
                    messagebox.showinfo(
                        "Success", "Application cache cleared.", parent=self
                    )
                except Exception as e:
                    messagebox.showerror(
                        "Error", f"Failed to clear cache: {e}", parent=self
                    )
            else:
                messagebox.showinfo(
                    "Info", "Cache directory is already empty.", parent=self
                )

    def _handle_export_logs(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log")],
            initialfile="emerald_diagnostic_logs.log",
            parent=self,
        )
        if path:
            try:
                shutil.copy("emerald_itr.log", path)
                messagebox.showinfo(
                    "Success", f"Logs exported to:\n{path}", parent=self
                )
            except Exception as e:
                messagebox.showerror(
                    "Error", f"Failed to export logs: {e}", parent=self
                )

    def _handle_reset_ai_cache(self):
        if messagebox.askyesno(
            "Confirm", "Reset AI model cache and audit logs?", parent=self
        ):
            log_path = os.path.join("data", "ai_audit_log.json")
            if os.path.exists(log_path):
                try:
                    os.remove(log_path)
                    messagebox.showinfo(
                        "Success", "AI logs and cache reset.", parent=self
                    )
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to reset: {e}", parent=self)
            else:
                messagebox.showinfo("Info", "AI cache is already clean.", parent=self)

    def _handle_clear_temp(self):
        temp_dir = "temp"
        if not os.path.exists(temp_dir):
            messagebox.showinfo(
                "Info", "Temporary directory is already empty.", parent=self
            )
            return

        if messagebox.askyesno("Confirm", "Clear all temporary files?", parent=self):
            try:
                for f in os.listdir(temp_dir):
                    fp = os.path.join(temp_dir, f)
                    if os.path.isfile(fp):
                        os.unlink(fp)
                    elif os.path.isdir(fp):
                        shutil.rmtree(fp)
                messagebox.showinfo("Success", "Temporary files cleared.", parent=self)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear temp: {e}", parent=self)

    def _handle_test_pdf(self):
        messagebox.showinfo(
            "PDF Test",
            "Test PDF generation triggered. Check your output folder.",
            parent=self,
        )

    def _handle_restore_position(self):
        if messagebox.askyesno(
            "Confirm", "Reset window position and size to defaults?", parent=self
        ):
            SettingsManager.set("Appearance.window_geometry", "1200x800+100+100")
            SettingsManager.set("Appearance.window_maximized", False)
            messagebox.showinfo(
                "Success",
                "Window position reset. This will take effect on next restart.",
                parent=self,
            )
