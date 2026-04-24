import customtkinter as ctk
from src.gui.styles.theme import Theme
from src.gui.widgets.common import make_card, page_header
from src.gui.styles.constants import (
    SPACING_XS,
    SPACING_SM,
    SPACING_MD,
    ENTRY_HEIGHT,
    RADIUS_MD,
    CARD_PADX,
    INNER_PADX,
    CHECKBOX_SIZE,
    CHECKBOX_SIZE_SM,
    DIVIDER_HEIGHT,
)


class ProfileConfigurator:
    ITR_INFO = {
        "ITR-1": {
            "name": "ITR-1 (Sahaj)",
            "description": "Salary up to ₹50L, max 2 house properties, LTCG u/s 112A up to ₹1.25L",
            "eligible": [
                "Salary",
                "HP (max 2)",
                "Other Sources",
            ],
            "not_eligible": ["Business", "Taxable Capital Gains", "STCG", "VDA"],
        },
        "ITR-2": {
            "name": "ITR-2",
            "description": "Salary + Capital Gains, no business income",
            "eligible": [
                "Salary",
                "House Property",
                "Other Sources",
                "Capital Gains",
            ],
            "not_eligible": ["Business / Profession"],
        },
        "ITR-3": {
            "name": "ITR-3 (Professional)",
            "description": "Business with books or Presumptive; all income",
            "eligible": [
                "Salary",
                "Business",
                "HP",
                "Other Sources",
                "Capital Gains",
            ],
            "not_eligible": [],
        },
        "ITR-4": {
            "name": "ITR-4 (Sugam)",
            "description": "Presumptive business, LTCG u/s 112A up to ₹1.25L",
            "eligible": [
                "Salary",
                "Presumptive Business",
                "HP (max 2)",
                "Other Sources",
            ],
            "not_eligible": ["Taxable Capital Gains", "STCG", "VDA"],
        },
    }

    def __init__(self, parent, on_profile_change, initial_itr="ITR-4", register_trace=None):
        self.parent = parent
        self.on_profile_change = on_profile_change
        self.register_trace = register_trace
        self.profile_config = {
            "has_salary": ctk.BooleanVar(value=False),
            "has_business": ctk.BooleanVar(value=False),
            "has_house_property": ctk.BooleanVar(value=False),
            "has_other_sources": ctk.BooleanVar(value=False),
            "has_capital_gains": ctk.BooleanVar(value=False),
            "has_stcg": ctk.BooleanVar(value=False),
            "has_ltcg": ctk.BooleanVar(value=False),
            "has_vda": ctk.BooleanVar(value=False),
            "business_type": ctk.StringVar(value="Presumptive (44AD / 44ADA)"),
            "itr_type": ctk.StringVar(value=initial_itr),
        }
        self.widgets = {}
        self._applying_constraints = False
        self._trace_tokens = []
        for v in self.profile_config.values():
            if hasattr(v, "trace_add"):
                if self.register_trace:
                    token = self.register_trace(v, "write", self._on_change)
                    if token:
                        self._trace_tokens.append((v, "write", token))
                else:
                    token = v.trace_add("write", self._on_change)
                    self._trace_tokens.append((v, "write", token))

    def _on_change(self, *_args):
        if self._applying_constraints:
            return
        self._apply_constraints()
        if self.on_profile_change:
            self.on_profile_change(self.get_profile_config())

    def _apply_constraints(self):
        self._applying_constraints = True
        try:
            it = self.profile_config["itr_type"].get()

            def _set_state(key, eligible):
                if key in self.widgets:
                    state = "normal" if eligible else "disabled"
                    color = Theme.TEXT_PRIMARY if eligible else Theme.TEXT_DIM
                    self.widgets[key].configure(state=state, text_color=color)
                    if not eligible:
                        self.profile_config[key].set(False)

            if it == "ITR-1":
                _set_state("has_business", False)
                _set_state("has_stcg", False)
                _set_state("has_vda", False)
                _set_state("has_capital_gains", True)
            elif it == "ITR-2":
                _set_state("has_business", False)
                _set_state("has_capital_gains", True)
                _set_state("has_stcg", True)
                _set_state("has_vda", True)
            elif it == "ITR-4":
                _set_state("has_stcg", False)
                _set_state("has_vda", False)
                _set_state("has_business", True)
            else:
                for k in [
                    "has_business",
                    "has_capital_gains",
                    "has_stcg",
                    "has_ltcg",
                    "has_vda",
                ]:
                    _set_state(k, True)

        except Exception as e:
            from src.services.logging_service import log as logger
            logger.error(f"Constraint application failed: {e}")
        finally:
            self._applying_constraints = False

    def get_profile_config(self):
        return {k: v.get() for k, v in self.profile_config.items()}

    def set_profile_config(self, config):
        for k, v in config.items():
            if k in self.profile_config:
                self.profile_config[k].set(v)

    def cleanup(self):
        for var, mode, token in self._trace_tokens:
            try:
                var.trace_remove(mode, token)
            except (ValueError, RuntimeError):
                pass
        self._trace_tokens.clear()

    @staticmethod
    def create_frame(parent, on_profile_change, initial_itr="ITR-4", register_trace=None):
        cf = ProfileConfigurator(parent, on_profile_change, initial_itr, register_trace)
        f = ctk.CTkFrame(parent, fg_color="transparent")
        page_header(f, "PROFILE CONFIGURATOR", "Select ITR type and applicable income sources.")
        ifr = make_card(f, "QUICK SETUP PRESETS")

        def apply_preset(p):
            presets = {
                "Salaried": {
                    "itr_type": "ITR-1",
                    "has_salary": True,
                    "has_business": False,
                    "has_house_property": False,
                    "has_capital_gains": False,
                    "has_other_sources": True,
                },
                "Business (44AD)": {
                    "itr_type": "ITR-4",
                    "has_salary": False,
                    "has_business": True,
                    "has_house_property": False,
                    "has_capital_gains": False,
                    "has_other_sources": True,
                    "business_type": "Presumptive (44AD / 44ADA)",
                },
                "Professional (44ADA)": {
                    "itr_type": "ITR-4",
                    "has_salary": False,
                    "has_business": True,
                    "has_house_property": False,
                    "has_capital_gains": False,
                    "has_other_sources": True,
                    "business_type": "Presumptive (44AD / 44ADA)",
                },
                "Investor (CG)": {
                    "itr_type": "ITR-2",
                    "has_salary": True,
                    "has_business": False,
                    "has_house_property": True,
                    "has_capital_gains": True,
                    "has_stcg": True,
                    "has_ltcg": True,
                    "has_other_sources": True,
                },
            }
            if p in presets:
                cf.set_profile_config(presets[p])

        ctk.CTkComboBox(
            ifr,
            values=[
                "Custom",
                "Salaried",
                "Business (44AD)",
                "Professional (44ADA)",
                "Investor (CG)",
            ],
            command=apply_preset,
            height=ENTRY_HEIGHT,
            font=Theme.BODY,
            **Theme.get_combo_style(),
        ).pack(pady=SPACING_XS, padx=INNER_PADX, fill="x")
        ctk.CTkFrame(ifr, height=DIVIDER_HEIGHT, fg_color=Theme.SECTION_BORDER).pack(fill="x", padx=INNER_PADX, pady=SPACING_SM)
        ctk.CTkLabel(ifr, text="ITR TYPE", font=Theme.H3, text_color=Theme.ACCENT_PRIMARY, anchor="w").pack(pady=(0, SPACING_XS), padx=INNER_PADX, anchor="w")
        il = ctk.CTkLabel(
            ifr,
            text="",
            font=Theme.BODY,
            text_color=Theme.TEXT_DIM,
            wraplength=600,
            anchor="w"
        )
        il.pack(pady=SPACING_XS, padx=INNER_PADX, anchor="w")
        ctk.CTkComboBox(
            ifr,
            values=["ITR-1", "ITR-2", "ITR-3", "ITR-4"],
            variable=cf.profile_config["itr_type"],
            height=ENTRY_HEIGHT,
            font=Theme.BODY,
            **Theme.get_combo_style(),
        ).pack(pady=SPACING_XS, padx=INNER_PADX, fill="x")
        ctk.CTkFrame(ifr, height=SPACING_SM, fg_color="transparent").pack()

        def upd(*_args):
            i = cf.profile_config["itr_type"].get()
            info = ProfileConfigurator.ITR_INFO.get(i, {})
            il.configure(
                text=(
                    f"{info.get('description', '')}\n\n"
                    f"✓ Eligible: {', '.join(info.get('eligible', []))}\n"
                    f"✗ Not Eligible: "
                    f"{', '.join(info.get('not_eligible', ['—']))}"
                ),
                justify="left",
            )
            cf._apply_constraints()

        if cf.register_trace:
            token = cf.register_trace(cf.profile_config["itr_type"], "write", upd)
            if token:
                cf._trace_tokens.append((cf.profile_config["itr_type"], "write", token))
        else:
            token = cf.profile_config["itr_type"].trace_add("write", upd)
            cf._trace_tokens.append((cf.profile_config["itr_type"], "write", token))
        upd()
        incf = make_card(f, "INCOME SOURCES", title_color=Theme.ACCENT_PRIMARY)
        income_sources = [
            ("has_salary", "Salary"),
            ("has_business", "Business / Profession"),
            ("has_house_property", "House Property"),
            ("has_other_sources", "Other Sources"),
            ("has_capital_gains", "Capital Gains"),
        ]
        for k, t in income_sources:
            cb = ctk.CTkCheckBox(
                incf,
                text=t,
                variable=cf.profile_config[k],
                font=Theme.BODY,
                text_color=Theme.TEXT_PRIMARY,
                checkbox_width=CHECKBOX_SIZE,
                checkbox_height=CHECKBOX_SIZE,
                hover_color=Theme.SUCCESS_GREEN,
                fg_color=Theme.SUCCESS_GREEN,
            )
            cb.pack(pady=SPACING_XS, padx=INNER_PADX, anchor="w")
            cf.widgets[k] = cb
        csf = ctk.CTkFrame(incf, fg_color="transparent")
        for k, t in [
            ("has_stcg", "STCG  (u/s 111A)"),
            ("has_ltcg", "LTCG  (u/s 112A)"),
            ("has_vda", "VDA / Crypto"),
        ]:
            cb = ctk.CTkCheckBox(
                csf,
                text=f"   → {t}",
                variable=cf.profile_config[k],
                font=Theme.BODY,
                text_color=Theme.TEXT_PRIMARY,
                checkbox_width=CHECKBOX_SIZE_SM,
                checkbox_height=CHECKBOX_SIZE_SM,
                hover_color=Theme.SUCCESS_GREEN,
                fg_color=Theme.SUCCESS_GREEN,
            )
            cb.pack(pady=SPACING_XS, padx=INNER_PADX + 20, anchor="w")
            cf.widgets[k] = cb
        ctk.CTkFrame(incf, height=SPACING_SM, fg_color="transparent").pack()
        btf = make_card(f, "BUSINESS TYPE", title_color=Theme.BRAND_BLUE)
        ctk.CTkComboBox(
            btf,
            values=[
                "Presumptive (44AD / 44ADA)",
                "Regular (with Books of Accounts)",
            ],
            variable=cf.profile_config["business_type"],
            height=ENTRY_HEIGHT,
            font=Theme.BODY,
            **Theme.get_combo_style(),
        ).pack(pady=SPACING_XS, padx=INNER_PADX, fill="x")
        ctk.CTkFrame(btf, height=SPACING_SM, fg_color="transparent").pack()

        def uv(*_args):
            show_cg = cf.profile_config["has_capital_gains"].get()
            show_biz = cf.profile_config["has_business"].get() and cf.profile_config[
                "itr_type"
            ].get() in [
                "ITR-3",
                "ITR-4",
            ]
            if show_cg:
                csf.pack(fill="x", padx=0, pady=0)
            else:
                csf.pack_forget()
            if show_biz:
                btf.pack(fill="x", padx=CARD_PADX, pady=(0, SPACING_SM))
            else:
                btf.pack_forget()

        if cf.register_trace:
            for var in [cf.profile_config["has_capital_gains"], cf.profile_config["has_business"], cf.profile_config["itr_type"]]:
                token = cf.register_trace(var, "write", uv)
                if token:
                    cf._trace_tokens.append((var, "write", token))
        else:
            for var in [cf.profile_config["has_capital_gains"], cf.profile_config["has_business"], cf.profile_config["itr_type"]]:
                token = var.trace_add("write", uv)
                cf._trace_tokens.append((var, "write", token))
        uv()
        f.configurator = cf
        return f
