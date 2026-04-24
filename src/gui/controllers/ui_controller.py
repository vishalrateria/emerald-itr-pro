from typing import Any, Dict
import customtkinter as ctk
from src.services.logging_service import log as logger
from src.gui.styles.theme import Theme

class UIController:
    def __init__(self, app_instance: Any):
        self.app = app_instance

    def update_status_bar(self, tax: float, paid: float) -> None:
        try:
            net = tax - paid
            color = Theme.ERROR_RED if net > 0 else Theme.SUCCESS_GREEN
            if "strip_tax" in self.app._strip_labels:
                self.app._strip_labels["strip_tax"].configure(
                    text=f"\u20b9 {int(tax):,}",
                    text_color=color
                )
            if "strip_net" in self.app._strip_labels:
                self.app._strip_labels["strip_net"].configure(
                    text=f"\u20b9 {int(net):,}",
                    text_color=color
                )
        except Exception as e:
            logger.error(f"UI Status Update Failed: {e}")

    def refresh_navigation(self, current_key: str) -> None:
        pass

    def update_window_title(self, client_name: str, itr_type: str) -> None:
        self.app.title(f"Emerald ITR Pro | {client_name} | {itr_type} | AY 2026-27")
