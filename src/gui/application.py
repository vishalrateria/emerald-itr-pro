import re
import tkinter as tk
from datetime import datetime
from tkinter import messagebox
import customtkinter as ctk
from src.config import (
    AUTOSAVE_INTERVAL,
    STD_DEDUCTION_NEW_REGIME,
    APP_VERSION,
    AY_CYCLE,
    DEFAULT_DEBOUNCE_INTERVAL,
    CONNECTIVITY_CHECK_INTERVAL,
)
from src.gui.styles.constants import (
    BUTTON_HEIGHT,
    BUTTON_HEIGHT_MD,
    ACTION_BUTTON_WIDTH_XL,
    ACTION_BUTTON_WIDTH_MD,
    DIVIDER_HEIGHT,
    SPACING_XL,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XS,
)
from src.services.logging_service import log as logger
from src.services.io.project_service import ProjectService
from src.services.io.export_service import ExportService
from src.services.settings_service import SettingsManager
from src.core.utils.backups import perform_rolling_backup
from src.gui.controllers.ui_controller import UIController
from src.gui.dialogs.dialog_factory import DialogFactory
from src.gui.dialogs.client_master_view import ClientMaster
from src.gui.controllers.state_registry import StateRegistry
from src.gui.controllers.tax_controller import TaxController
from src.gui.views.setup.profile_view import ProfileConfigurator
from src.gui.dialogs.settings_view import SettingsDialog
from src.gui.styles.theme import Theme
from src.gui.views import (
    BalanceSheetSchedule,
    BusinessFinancialsSchedule,
    DeductionsSchedule,
    ExemptIncomeSchedule,
    ForeignAssetsSchedule,
    HousePropertySchedule,
    LTCGSchedule,
    MasterSchedule,
    OtherSourcesSchedule,
    PersonalSchedule,
    Presumptive44ADSchedule,
    Presumptive44ADASchedule,
    Presumptive44AESchedule,
    SalarySchedule,
    STCGSchedule,
    TaxPaidSchedule,
    TrialBalanceSchedule,
    VDASchedule,
    VerifySchedule,
    WizardSchedule,
    AuditSchedule,
)
from src.gui.core.app_state import VarDict
from src.gui.core.history_manager import HistoryManager
from src.gui.core.autosave_manager import AutosaveMixin
from src.gui.navigation.navigator import NavigatorMixin
from src.gui.layout.main_layout import MainLayoutMixin
from src.gui.layout.navbar import NavbarMixin
from src.gui.layout.status_bar import StatusBarMixin
from src.gui.layout.summary_bar import SummaryBarMixin


class EmeraldITRMain(
    AutosaveMixin,
    NavigatorMixin,
    MainLayoutMixin,
    NavbarMixin,
    StatusBarMixin,
    SummaryBarMixin,
    ctk.CTk,
):
    def __init__(self):
        ctk.CTk.__init__(self)
        self.VERSION = APP_VERSION
        self._settings = SettingsManager.load()
        self.history = HistoryManager(self)
        _title_prefix = SettingsManager.get(
            "General.app_title_prefix", "EMERALD ITR PRO"
        )
        self.title(
            f"{_title_prefix} {self.VERSION}  |  Indian Tax Utility ({AY_CYCLE})"
        )
        self._connectivity_thread = None
        self._connectivity_timer = None
        try:
            _bk_folder = SettingsManager.get("Data.backup_folder", "backups/clients")
            _max_bk = int(SettingsManager.get("Data.max_rolling_backups", 5))
            perform_rolling_backup("clients", _bk_folder, max_backups=_max_bk)
        except Exception as e:
            logger.warning(f"Startup backup skipped: {e}")
        Theme.set_theme_mode()
        self.configure(fg_color=Theme.BG_PRIMARY)
        self._trace_callbacks = []
        self._state_registry = StateRegistry(self)
        self._tax_controller = TaxController(self)
        self._ui_controller = UIController(self)
        self.profile_configurator = None
        self.selected_itr_type = SettingsManager.get("General.default_itr_type")
        self.vars = VarDict()
        self.frames = {}
        self.dynamic_refs = {}
        self.validation_refs = {}
        self.summary_labels = {}
        self.step_buttons = {}
        self.step_visibility = {}
        self._recompute_timer = None
        self._needs_save = False
        self._recomputing = False
        self._suppress_recompute = False
        self._autosave_job = None
        self._autosave_timer = None
        ProjectService.progress_callback = self.update_progress_ui
        self.init_core_vars()
        self.setup_input_validators()
        self.setup_layout()
        self.setup_keyboard_shortcuts()
        Theme.apply_dark_title_bar(self)
        self.update_window_title(self.selected_itr_type)
        self.update_dashboard_visibility()
        saved_geometry = SettingsManager.get("Appearance.window_geometry")
        if saved_geometry:
            self.geometry(saved_geometry)
        if SettingsManager.get("Appearance.window_maximized", True):
            self.after(50, lambda: self.state("zoomed"))
        _as_ms = SettingsManager.get("Data.autosave_interval_ms", AUTOSAVE_INTERVAL)
        self._current_autosave_ms = _as_ms
        if _as_ms and _as_ms > 0:
            self._autosave_job = self.after(_as_ms, self.perform_autosave)

    @property
    def needs_save(self):
        return self._needs_save

    @needs_save.setter
    def needs_save(self, value):
        if self._needs_save != value:
            self._needs_save = value
            self.update_window_title()
            if not value:
                ts = datetime.now().strftime("%H:%M:%S")
                self.save_status_label.configure(text=f"Last Saved: {ts}")

    def register_trace(self, var, mode, callback):
        token = var.trace_add(mode, callback)
        self._trace_callbacks.append((var, mode, token))
        return token

    def clear_traces(self):
        for var, mode, token in self._trace_callbacks:
            try:
                var.trace_remove(mode, token)
            except (ValueError, RuntimeError, tk.TclError) as e:
                logger.debug(f"Trace removal skipped: {e}")
        self._trace_callbacks.clear()

    def init_core_vars(self):
        self.vars.update(self._state_registry.initialize_vars(self.selected_itr_type))
        self.apply_all_traces()

    def apply_all_traces(self):
        def make_history_callback(key, var):
            old = var.get()

            def _trace(*_args):
                nonlocal old
                new = var.get()
                if old != new:
                    self.history.record(key, old, new)
                    old = new

            return _trace

        def make_recompute_callback():
            def _trace(*_args):
                self.live_recompute()

            return _trace

        for k, v in self.vars.items():
            self.register_trace(v, "write", make_history_callback(k, v))
            if k in self._state_registry.traced_keys:
                self.register_trace(v, "write", make_recompute_callback())
        self.setup_input_validators()

    def setup_input_validators(self):
        _guarding: set = set()

        def _update_validation_ui(key, is_valid):
            w = self.validation_refs.get(key)
            if w:
                w.configure(
                    border_color=Theme.SECTION_BORDER if is_valid else Theme.ERROR_RED
                )
            if is_valid:
                self.status_text.configure(
                    text="Engine Ready", text_color=Theme.TEXT_PRIMARY
                )
                self.status_dot.configure(text_color=Theme.SUCCESS_GREEN)
            else:
                self.status_text.configure(
                    text=f"Invalid {key.upper()}", text_color=Theme.ERROR_RED
                )
                self.status_dot.configure(text_color=Theme.ERROR_RED)

        def _make_filter(key, filter_fn, regex=None):
            def _filter(*_):
                if key in _guarding:
                    return
                v = self.vars.get(key)
                if v:
                    raw = v.get()
                    cleaned = filter_fn(raw)
                    if cleaned != raw:
                        _guarding.add(key)
                        v.set(cleaned)
                        _guarding.discard(key)
                    if regex and cleaned:
                        _update_validation_ui(key, bool(re.match(regex, cleaned)))

            return _filter

        validators = [
            (
                "pan",
                lambda s: "".join(c for c in s if c.isalnum()).upper()[:10],
                r"^[A-Z]{3}[PCFATHBLJG][A-Z][0-9]{4}[A-Z]$",
            ),
            (
                "aadhaar",
                lambda s: "".join(c for c in s if c.isdigit())[:12],
                r"^[0-9]{12}$",
            ),
            (
                "email",
                lambda s: "".join(c for c in s if c.isprintable()).strip(),
                r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
            ),
            (
                "mobile",
                lambda s: "".join(c for c in s if c.isdigit())[:10],
                r"^[6789][0-9]{9}$",
            ),
        ]
        for key, filter_fn, regex in validators:
            self.register_trace(
                self.vars[key], "write", _make_filter(key, filter_fn, regex)
            )

    def init_frames(self):
        self._setup_welcome_screen()
        self.get_or_create_frame("profile_config")
        self.update_wizard_steps()
        if self.client_master and self.client_master.current_client_id:
            self.go_to_step(0)
        else:
            self.show_welcome_screen()

    def _setup_welcome_screen(self):
        self.welcome_frame = ctk.CTkFrame(
            self.scrollable_content, fg_color="transparent"
        )
        inner = ctk.CTkFrame(
            self.welcome_frame,
            fg_color=Theme.BG_SECONDARY,
            corner_radius=Theme.RADIUS_LG,
            border_width=1,
            border_color=Theme.SECTION_BORDER,
            width=650,
            height=350,
        )
        inner.pack(pady=SPACING_XL, padx=SPACING_LG, expand=True)
        inner.pack_propagate(False)
        inner.pack_propagate(False)
        ctk.CTkLabel(
            inner,
            text="Welcome to Emerald ITR Pro",
            font=Theme.H1,
            text_color=Theme.BRAND_BLUE,
        ).pack(pady=SPACING_XS)
        ctk.CTkLabel(
            inner,
            text="Production Grade Indian Tax Utility  ·  AY 2026-27",
            font=Theme.BODY,
            text_color=Theme.TEXT_DIM,
            wraplength=700,
        ).pack(pady=(0, SPACING_SM))
        btn_f = ctk.CTkFrame(inner, fg_color="transparent")
        btn_f.pack(pady=SPACING_SM)
        ctk.CTkButton(
            btn_f,
            text="+ Create New Client",
            width=ACTION_BUTTON_WIDTH_XL,
            height=BUTTON_HEIGHT,
            font=Theme.BODY_BOLD,
            command=lambda: self.handle_add_client(self.client_master),
            **Theme.get_button_style("primary"),
        ).pack(side="left", padx=SPACING_SM)
        ctk.CTkButton(
            btn_f,
            text="Open Database",
            width=ACTION_BUTTON_WIDTH_XL,
            height=BUTTON_HEIGHT,
            font=Theme.BODY_BOLD,
            command=self.show_client_manager,
            **Theme.get_button_style("secondary"),
        ).pack(side="left", padx=SPACING_SM)
        recents = SettingsManager.get("General.recent_clients", [])
        if recents and self.client_master:
            ctk.CTkLabel(
                inner,
                text="RECENT TAXPAYERS",
                font=Theme.CAPTION,
                text_color=Theme.TEXT_DIM,
            ).pack(pady=(SPACING_LG, SPACING_XS))
            recent_f = ctk.CTkFrame(inner, fg_color="transparent")
            recent_f.pack(pady=(0, SPACING_LG))
            for cid in recents:
                cd = self.client_master.clients.get(cid)
                if cd:
                    ctk.CTkButton(
                        recent_f,
                        text=cd["name"],
                        font=Theme.CAPTION,
                        width=ACTION_BUTTON_WIDTH_MD,
                        height=BUTTON_HEIGHT_MD,
                        command=lambda c=cid: self.handle_client_switch(c),
                        **Theme.get_button_style("ghost"),
                    ).pack(side="left", padx=SPACING_XS)
        ctk.CTkFrame(inner, fg_color="transparent", height=1).pack(
            expand=True, fill="both"
        )
        tip_f = ctk.CTkFrame(
            inner, fg_color=Theme.BG_INPUT, corner_radius=Theme.RADIUS_SM
        )
        tip_f.pack(pady=(0, SPACING_SM), padx=SPACING_MD, fill="x")
        ctk.CTkLabel(
            tip_f,
            text="Quick Tip: Use Ctrl+T to jump to the Master Computation Dashboard at any time.",
            font=Theme.CAPTION,
            text_color=Theme.TEXT_MUTED,
        ).pack(pady=SPACING_XS)

    def show_welcome_screen(self):
        self.footer.grid_forget()
        for f in self.frames.values():
            f.pack_forget()
        self.welcome_frame.pack(fill="both", expand=True)
        for b_tuple in self.step_buttons.values():
            b_tuple[0].configure(state="disabled")
        self.footer.grid_remove()

    def show_client_manager(self):
        if self.client_master:
            self.client_master.show_manager_dialog()

    def get_or_create_frame(self, key):
        if key in self.frames:
            return self.frames[key]
        f = None
        if key == "profile_config":
            f = ProfileConfigurator.create_frame(
                self.scrollable_content,
                on_profile_change=self.handle_profile_config_change,
                initial_itr=self.selected_itr_type,
                register_trace=self.register_trace,
            )
            self.profile_configurator = f.configurator
        elif key == "personal":
            f = PersonalSchedule.create_frame(
                self.scrollable_content,
                self.vars,
                self.dynamic_refs,
                self.validation_refs,
            )
        elif key == "master":
            f = MasterSchedule.create_frame(
                self.scrollable_content, self.vars, self.show_frame, self.summary_labels
            )
        elif key == "salary":
            f = SalarySchedule.create_frame(
                self.scrollable_content, self.vars, self.validation_refs
            )
        elif key == "hp":
            f = HousePropertySchedule.create_frame(
                self.scrollable_content, self.vars, self.validation_refs
            )
        elif key == "other_sources":
            f = OtherSourcesSchedule.create_frame(
                self.scrollable_content,
                self.vars,
                self.summary_labels,
                self.validation_refs,
                itr_type=self.selected_itr_type,
            )
        elif key == "business_financials":
            f = BusinessFinancialsSchedule.create_frame(
                self.scrollable_content, self.vars
            )
        elif key == "44ad":
            f = Presumptive44ADSchedule.create_frame(
                self.scrollable_content,
                self.vars,
                self.summary_labels,
                self.validation_refs,
            )
        elif key == "44ada":
            f = Presumptive44ADASchedule.create_frame(
                self.scrollable_content,
                self.vars,
                self.summary_labels,
                self.validation_refs,
            )
        elif key == "44ae":
            f = Presumptive44AESchedule.create_frame(
                self.scrollable_content,
                self.vars,
                self.summary_labels,
                self.validation_refs,
            )
        elif key == "tb":
            f = TrialBalanceSchedule.create_frame(
                self.scrollable_content, self.vars, self.summary_labels
            )
        elif key == "bs":
            f = BalanceSheetSchedule.create_frame(
                self.scrollable_content, self.vars, self.summary_labels
            )
        elif key == "stcg":
            f = STCGSchedule.create_frame(
                self.scrollable_content,
                self.vars,
                self.summary_labels,
                self.validation_refs,
            )
        elif key == "ltcg":
            f = LTCGSchedule.create_frame(
                self.scrollable_content,
                self.vars,
                self.summary_labels,
                self.validation_refs,
            )
        elif key == "vda":
            f = VDASchedule.create_frame(
                self.scrollable_content,
                self.vars,
                self.validation_refs,
                settings=self._settings,
            )
        elif key == "fa":
            f = ForeignAssetsSchedule.create_frame(self.scrollable_content, self.vars)
        elif key == "deductions":
            f = DeductionsSchedule.create_frame(
                self.scrollable_content, self.vars, self.validation_refs
            )
        elif key == "exempt":
            f = ExemptIncomeSchedule.create_frame(self.scrollable_content, self.vars)
        elif key == "tax":
            f = TaxPaidSchedule.create_frame(
                self.scrollable_content,
                self.vars,
                self.validation_refs,
                settings=self._settings,
            )
        elif key == "verify":
            f = VerifySchedule.create_frame(self.scrollable_content, self.vars)
        elif key == "wizard":
            f = WizardSchedule.create_frame(self.scrollable_content, self.vars)
        elif key == "audit_workspace":
            f = AuditSchedule.create_frame(self.scrollable_content, self.vars)
        if f:
            self.frames[key] = f
            return f
        return None

    def live_recompute(self):
        if not SettingsManager.get("Engine.enable_live_recompute", True):
            return
        if self._recompute_timer:
            self.after_cancel(self._recompute_timer)
        _debounce = SettingsManager.get(
            "Engine.debounce_interval_ms", DEFAULT_DEBOUNCE_INTERVAL
        )
        self._recompute_timer = self.after(_debounce, self._perform_live_recompute)
        self.trigger_autosave_debounce()

    def update_progress_ui(self, val):
        self.compute_progress.set(val / 100.0)
        self.update_idletasks()

    def _perform_live_recompute(self):
        if self._recomputing or self._suppress_recompute:
            return
        self._recomputing = True
        self.needs_save = True
        self.status_dot.configure(text_color=Theme.WARNING)
        self.status_text.configure(text="Computing…")
        self.compute_progress.pack(side="left", padx=4)
        self.compute_progress.start()
        self.update_idletasks()
        try:
            self._tax_controller.compute()
            self.update_summary_strip()
            self.update_summary_labels()
            self.run_audit_diagnostics()
        except Exception as e:
            logger.error(f"Recompute error: {e}")
        finally:
            self.status_dot.configure(text_color=Theme.SUCCESS_GREEN)
            self.status_text.configure(text="Ready")
            self.compute_progress.stop()
            self.compute_progress.pack_forget()
            self._recomputing = False

    def update_summary_labels(self):
        for key, lbl in self.summary_labels.items():
            lookup_key = (
                key.replace("audit_ret_", "") if key.startswith("audit_ret_") else key
            )
            if lookup_key in self.vars and isinstance(lbl, ctk.CTkLabel):
                val = self.vars[lookup_key].get() or "0"
                try:
                    fval = float(str(val).replace(",", ""))
                    if key == "tax_net":
                        if fval < 0:
                            lbl.configure(
                                text=f"REFUND: ₹ {abs(int(fval)):,}",
                                text_color=Theme.SUCCESS_GREEN,
                            )
                        else:
                            lbl.configure(
                                text=f"PAYABLE: ₹ {int(fval):,}",
                                text_color=(
                                    Theme.ERROR_RED if fval > 0 else Theme.TEXT_PRIMARY
                                ),
                            )
                    elif key.startswith("audit_ret_"):
                        lbl.configure(text=f"₹ {int(fval):,}")
                        stat_lbl = self.summary_labels.get(f"audit_stat_{lookup_key}")
                        if stat_lbl:
                            ais_val = getattr(stat_lbl, "_ais_val", 0)
                            diff = abs(fval - ais_val)
                            if diff < 10:
                                stat_lbl.configure(
                                    text="MATCHED", text_color=Theme.SUCCESS_GREEN
                                )
                            else:
                                stat_lbl.configure(
                                    text=f"MISMATCH (₹{int(diff):,})",
                                    text_color=Theme.ERROR_RED,
                                )
                    else:
                        lbl.configure(text=f"₹ {int(fval):,}")
                except Exception:
                    lbl.configure(text=str(val))

    def run_audit_diagnostics(self):
        log_frame = self.summary_labels.get("audit_log")
        if not log_frame:
            return
        for w in log_frame.winfo_children():
            w.destroy()
        issues = []
        try:
            gti_val = float(
                str(
                    self.vars.get("gti", ctk.StringVar(value="0")).get() or "0"
                ).replace(",", "")
            )
            if gti_val <= 0:
                issues.append(
                    (
                        "CRITICAL: No income data found for AY 2026-27",
                        "income_salary",
                        Theme.ERROR_RED,
                    )
                )
            tax_paid = float(
                str(
                    self.vars.get("it_total", ctk.StringVar(value="0")).get() or "0"
                ).replace(",", "")
            )
            tax_due = float(
                str(
                    self.vars.get("tax_total", ctk.StringVar(value="0")).get() or "0"
                ).replace(",", "")
            )
            if tax_due > 0 and tax_paid == 0:
                issues.append(
                    (
                        "WARNING: Tax payable but zero tax credits found",
                        "taxes",
                        Theme.TAX_AMBER,
                    )
                )
            ded_80c = float(
                str(
                    self.vars.get("ded_80c", ctk.StringVar(value="0")).get() or "0"
                ).replace(",", "")
            )
            if ded_80c > 150000:
                issues.append(
                    (
                        "LIMIT: Sec 80C deductions capped at ₹1,50,000",
                        "deductions",
                        Theme.TAX_AMBER,
                    )
                )
        except Exception as e:
            logger.debug(f"Audit computation error: {e}")
        if issues:
            for msg, target, color in issues:
                row = ctk.CTkFrame(log_frame, fg_color="transparent", cursor="hand2")
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text="●", font=Theme.ICON_SM, text_color=color).pack(
                    side="left", padx=5
                )
                lbl = ctk.CTkLabel(
                    row,
                    text=msg,
                    font=Theme.CAPTION,
                    text_color=Theme.TEXT_PRIMARY,
                    anchor="w",
                )
                lbl.pack(side="left", fill="x", expand=True)
                ctk.CTkLabel(
                    row,
                    text="FIX →",
                    font=Theme.CAPTION_BOLD,
                    text_color=Theme.ACCENT_PRIMARY,
                ).pack(side="right", padx=10)

                def _fix(e, t=target):
                    self.go_to_step_by_id(t)

                row.bind("<Button-1>", _fix)
                row.bind(
                    "<Enter>", lambda e, r=row: r.configure(fg_color=Theme.BG_HOVER)
                )
                row.bind(
                    "<Leave>", lambda e, r=row: r.configure(fg_color="transparent")
                )
        else:
            ctk.CTkLabel(
                log_frame,
                text="ALL STATUTORY CHECKS PASSED",
                font=Theme.CAPTION_BOLD,
                text_color=Theme.SUCCESS_GREEN,
            ).pack(pady=SPACING_SM)
            ctk.CTkButton(
                log_frame,
                text="Run AI Audit",
                font=Theme.CAPTION_BOLD,
                text_color=Theme.TEXT_PRIMARY,
                command=self.run_ai_audit_diagnostic,
            ).pack(pady=SPACING_SM)

    def run_ai_audit_diagnostic(self):
        from tkinter import messagebox
        from src.services.io.import_service import ImportService

        vardict = {
            "income": {
                "sal_gross": int(
                    str(
                        self.vars.get("sal_gross", ctk.StringVar(value="0")).get()
                        or "0"
                    ).replace(",", "")
                )
                or 0,
                "os_dividend": [],
                "total_income": int(
                    str(
                        self.vars.get("total_income", ctk.StringVar(value="0")).get()
                        or "0"
                    ).replace(",", "")
                )
                or 0,
            },
            "deductions": {
                "ded_16ia": int(
                    str(
                        self.vars.get("ded_16ia", ctk.StringVar(value="0")).get() or "0"
                    ).replace(",", "")
                )
                or 0
            },
            "schedules": {
                "schedule_al_populated": bool(
                    str(
                        self.vars.get("schedule_al", ctk.StringVar()).get() or ""
                    ).strip()
                )
            },
        }

        def on_result(result):
            if result.get("status") == "success":
                ai_data = result.get("data", {})
                warnings = ai_data.get("warnings", [])
                if warnings:
                    msg = "AI Audit Findings:\n\n"
                    for w in warnings[:10]:
                        msg += f"[{w.get('severity', 'Medium')}] {w.get('section', 'General')}\n"
                        msg += f"  {w.get('message', '')}\n"
                        if w.get("legal_ref"):
                            msg += f"  Ref: {w.get('legal_ref')}\n"
                        msg += "\n"
                    msg += f"\nConfidence: {ai_data.get('confidence', 0):.0%}"
                    messagebox.showinfo("AI Tax Audit", msg)
                else:
                    messagebox.showinfo(
                        "AI Tax Audit",
                        "No issues found by AI audit.\n\nYour return looks good!",
                    )
            elif result.get("status") == "disabled":
                messagebox.showwarning(
                    "AI Disabled", "AI is disabled. Enable it in Settings."
                )
            else:
                messagebox.showerror("AI Error", result.get("error", "Unknown error"))

        result = ImportService.run_ai_audit(
            vardict=vardict, root_window=self, on_result=on_result
        )
        if result is None:
            messagebox.showwarning("AI Unavailable", "AI services not available.")

    def handle_profile_config_change(self, profile_config):
        new_itr_type = profile_config.get("itr_type", self.selected_itr_type)
        if new_itr_type != self.selected_itr_type:
            self.selected_itr_type = new_itr_type
            self.update_window_title(new_itr_type)
        self.update_wizard_steps()
        self.update_dashboard_visibility()
        if self.client_master and self.client_master.current_client_id:
            self.client_master.update_client_profile_config(
                self.client_master.current_client_id, profile_config
            )

    def update_dashboard_visibility(self):
        config = (
            self.profile_configurator.get_profile_config()
            if self.profile_configurator
            else {}
        )

        def toggle(key, condition):
            row = self.summary_labels.get(f"row_{key}")
            if row:
                (row.grid(sticky="ew") if condition else row.grid_remove())

        for k in [
            "sal_total",
            "hp_total",
            "bp_total",
            "ltcg_112a_sum",
            "stcg_sum",
            "vda_sum",
            "os_total",
        ]:
            toggle(
                k, config.get(f"has_{k.replace('_total','').replace('_sum','')}", True)
            )

    def update_window_title(self, itr_type=None):
        itr_map = {
            "ITR-1": "SAHAJ",
            "ITR-2": "ITR-2",
            "ITR-3": "ITR-3",
            "ITR-4": "SUGAM",
        }
        name = itr_map.get(itr_type or self.selected_itr_type, "ITR")
        dirty = "*" if self._needs_save else ""
        self.title(f"{dirty}EMERALD ITR PRO {self.VERSION}  ·  {name}  ·  AY 2026-27")
        Theme.apply_dark_title_bar(self)

    def handle_client_dropdown_switch(self, selected_name):
        for cid, cd in self.client_master.clients.items():
            if cd["name"] in selected_name:
                self.handle_client_switch(cid)
                return

    def handle_client_switch(self, client_id):
        if self.client_master.set_current_client(client_id):
            client_data = self.client_master.get_client(client_id)
            self._suppress_recompute = True
            try:
                self.clear_traces()
                self._clear_vars_internal()
                logger.info(f"👤 Switching to client: {client_id}")
                for k, v in client_data.get("_form_cache", {}).items():
                    if k in self.vars:
                        self.vars[k].set(str(v))
                if "profile_config" in client_data:
                    config = client_data["profile_config"]
                    if self.profile_configurator:
                        self.profile_configurator.set_profile_config(config)
                    self.handle_profile_config_change(config)
            except Exception as e:
                logger.error(f"Client switch failed: {e}")
            finally:
                try:
                    self.apply_all_traces()
                except Exception as trace_err:
                    logger.error(f"Trace restoration failed: {trace_err}")
                self._suppress_recompute = False
            recents = SettingsManager.get("General.recent_clients", [])
            if client_id in recents:
                recents.remove(client_id)
            recents.insert(0, client_id)
            SettingsManager.set("General.recent_clients", recents[:3])
            self.update_client_dropdown()
            self.live_recompute()
            self.go_to_step(0)
            messagebox.showinfo("Switched", f"Switched to {client_data['name']}")

    def handle_html_report(self):
        if not self.client_master or not self.client_master.current_client_id:
            messagebox.showwarning("Warning", "Please select a taxpayer first.")
            return
        from src.services.io.report_service import ReportService

        cid = self.client_master.current_client_id
        client_data = self.client_master.clients[cid]
        tax_data = {
            k: float(str(v.get() or "0").replace(",", "") or "0")
            for k, v in self.vars.items()
            if hasattr(v, "get")
        }
        try:
            ReportService.generate_computation_report(
                client_data, tax_data, f"Comp_{cid}.html"
            )
            self.status_text.configure(
                text="Report Generated", text_color=Theme.SUCCESS_GREEN
            )
        except Exception as e:
            messagebox.showerror("Error", f"Report failed: {e}")

    def handle_save_and_switch(self, client_id):
        if self.needs_save:
            if messagebox.askyesno(
                "Unsaved Changes", "You have unsaved changes. Save before switching?"
            ):
                self.perform_autosave()
        self.handle_client_switch(client_id)

    def handle_add_client(self, client_master):
        ClientMaster.create_add_client_dialog(self, client_master)
        self.update_client_dropdown()

    def open_settings(self):
        SettingsDialog(self, on_settings_saved=self.handle_settings_saved)

    def handle_settings_saved(self, new_settings):
        self._settings = new_settings
        Theme.set_theme_mode()
        self.configure(fg_color=Theme.BG_PRIMARY)
        Theme.apply_dark_title_bar(self)
        self._refresh_ui_theme()
        if hasattr(self, "_autosave_job") and self._autosave_job:
            self.after_cancel(self._autosave_job)
            self._autosave_job = None
        _as_ms = SettingsManager.get("Data.autosave_interval_ms", AUTOSAVE_INTERVAL)
        if _as_ms > 0:
            self._autosave_job = self.after(_as_ms, self.perform_autosave)
        self.update_window_title(self.selected_itr_type)
        logger.info("⚙️ Settings updated and applied")

    def _refresh_ui_theme(self):
        try:
            for attr in ["navbar", "summary_bar", "sidebar", "footer"]:
                if hasattr(self, attr):
                    getattr(self, attr).configure(
                        fg_color=Theme.BG_SECONDARY, border_color=Theme.SECTION_BORDER
                    )
            if hasattr(self, "status_text"):
                self.status_text.configure(text_color=Theme.TEXT_DIM)
            if hasattr(self, "status_dot"):
                self.status_dot.configure(text_color=Theme.SUCCESS_GREEN)
        except Exception as e:
            logger.warning(f"UI theme refresh partial: {e}")

    def handle_export(self):
        ExportService.export_itr_json(
            self.vars, float(self.vars["gti"].get() or 0), self.selected_itr_type
        )

    def handle_pdf_draft(self):
        summary = {
            k: float(self.vars[v].get() or 0)
            for k, v in [
                ("gti", "gti"),
                ("tti", "tti"),
                ("tax", "due_tax"),
                ("paid", "it_total"),
            ]
        }
        summary["net"] = summary["tax"] - summary["paid"]
        ExportService.generate_pdf_draft(self.vars, summary)

    def show_backup_menu(self):
        DialogFactory.show_backup_menu(
            self,
            lambda: ProjectService.backup_data(self.vars),
            lambda: ProjectService.restore_data(self.vars),
        )

    def show_tax_calendar(self):
        DialogFactory.show_tax_calendar(self)

    def show_sync_menu(self):
        DialogFactory.show_sync_menu(self)

    def show_ai_panel(self, ai_data: dict = None):
        from src.gui.components.ai_panel import AIPanel, extract_suggestions_from_result
        from tkinter import messagebox

        ai_manager = None
        try:
            from src.services.ai.ai_manager import get_ai_manager

            ai_manager = get_ai_manager()
        except ImportError:
            messagebox.showerror("Error", "AI services not available")
            return
        if not ai_manager.is_enabled():
            messagebox.showwarning(
                "AI Disabled", "Enable AI in Settings to use this feature."
            )
            return
        dialog = ctk.CTkToplevel(self)
        dialog.title("AI Suggestions")
        dialog.geometry("500x600")
        dialog.transient(self)
        dialog.grab_set()
        ai_panel = AIPanel(dialog, root_window=self)
        ai_panel.pack(fill="both", expand=True, padx=10, pady=10)
        if ai_data:
            vardict = {
                k: v.get() if hasattr(v, "get") else v for k, v in self.vars.items()
            }
            suggestions = extract_suggestions_from_result(vardict, {"data": ai_data})
            for s in suggestions:
                ai_panel.add_suggestion(
                    field_name=s["field"],
                    current_value=s.get("current"),
                    ai_value=s.get("ai"),
                    confidence=s.get("confidence", 0.85),
                )

        def on_accept(field, value, _action):
            if field in self.vars:
                self.vars[field].set(str(int(value)))
                self.live_recompute()

        ai_panel.set_callback(on_accept)

    def clear_form(self):
        if self._needs_save:
            if not messagebox.askyesno(
                "Unsaved Changes", "Form has unsaved data. Discard and clear?"
            ):
                return
        if messagebox.askyesno("Clear All", "Reset all form data?"):
            self._suppress_recompute = True
            self._clear_vars_internal()
            self._suppress_recompute = False
            self.live_recompute()

    def _clear_vars_internal(self):
        for k, v in self.vars.items():
            if k == "sal_std_ded":
                v.set(str(STD_DEDUCTION_NEW_REGIME))
            elif k in [
                "pan",
                "aadhaar",
                "name",
                "dob",
                "status",
                "emp_cat",
                "filing_status",
                "email",
                "mobile",
            ]:
                v.set("")
            elif any(
                k.endswith(s)
                for s in ["_tan", "_name", "_date", "_pan", "_ifsc", "_acc"]
            ):
                v.set("")
            else:
                v.set("0")
        logger.debug("🧹 Form state cleared")

    def show_frame(self, key):
        for idx, step in enumerate(self.steps):
            if key in step["frames"]:
                self.go_to_step(idx)
                return

    def update_navigation_tree(self):
        self._ui_controller.refresh_navigation(self.steps[self.current_step_idx]["id"])

    def check_connectivity(self):
        import socket
        import threading

        def _check():
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=2)
                self.after_idle(
                    lambda: self.conn_label.configure(
                        text="● ONLINE", text_color=Theme.SUCCESS_GREEN
                    )
                )
            except (OSError, socket.error):
                self.after_idle(
                    lambda: self.conn_label.configure(
                        text="○ OFFLINE", text_color=Theme.ERROR_RED
                    )
                )
            self._connectivity_timer = self.after(
                CONNECTIVITY_CHECK_INTERVAL, self.check_connectivity
            )

        self._connectivity_thread = threading.Thread(target=_check, daemon=True)
        self._connectivity_thread.start()

    def setup_keyboard_shortcuts(self):
        self.bind("<Control-s>", lambda e: self.perform_autosave())
        self.bind("<Control-n>", lambda e: self.handle_add_client(self.client_master))
        self.bind("<Control-p>", lambda e: self.handle_pdf_draft())
        self.bind("<Control-z>", lambda e: self.history.undo())
        self.bind("<Control-y>", lambda e: self.history.redo())

    def on_close(self):
        for attr in ["_autosave_job", "_connectivity_timer"]:
            job = getattr(self, attr, None)
            if job:
                self.after_cancel(job)
        SettingsManager.set("Appearance.window_geometry", self.geometry())
        SettingsManager.set("Appearance.window_maximized", (self.state() == "zoomed"))
        self.destroy()


if __name__ == "__main__":
    app = EmeraldITRMain()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
