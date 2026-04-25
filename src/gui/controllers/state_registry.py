import tkinter as tk
from typing import Any, Dict
import customtkinter as ctk
from src.config import STD_DEDUCTION_NEW_REGIME
from src.gui.controllers.initializers import (
    init_personal_vars,
    init_income_vars,
    init_tax_deduction_vars,
    init_business_vars,
    init_schedule_vars,
    init_bank_vars,
    init_disclosure_vars,
)


class StateRegistry:
    def __init__(self, app_instance: Any):
        self.app = app_instance
        self.vars: Dict[str, tk.Variable] = {}
        self.traced_keys: set = set()

    def _traced(self, key: str, val: str = "0") -> tk.Variable:
        try:
            v = ctk.StringVar(value=val)
            self.app.register_trace(v, "write", lambda *a: self.app.live_recompute())
            self.traced_keys.add(key)
            return v
        except Exception as e:
            import logging

            logging.warning(f"Failed to trace variable: {e}")
            return ctk.StringVar(value=val)

    def initialize_vars(self, selected_itr_type: str) -> Dict[str, tk.Variable]:
        init_personal_vars(self.vars, self._traced)
        init_income_vars(self.vars, self._traced, selected_itr_type)
        init_tax_deduction_vars(self.vars, self._traced)
        init_business_vars(self.vars, self._traced)
        init_schedule_vars(self.vars, self._traced)
        init_bank_vars(self.vars, self._traced)
        init_disclosure_vars(self.vars, self._traced)
        return self.vars
