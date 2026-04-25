import json
import os
from typing import Any, Callable, Optional

try:
    import customtkinter as ctk

    CTK_AVAILABLE = True
except ImportError:
    CTK_AVAILABLE = False

from src.services.logging_service import log as logger
from src.services.ai.ai_manager import get_ai_manager, log_audit_decision
from src.gui.styles.theme import Theme


class AISuggestionItem(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        field_name: str,
        current_value: Any,
        ai_value: Any,
        confidence: float,
        source_snippet: str = "",
        on_accept: Callable = None,
        on_reject: Callable = None,
        **kwargs,
    ):
        super().__init__(parent, **kwargs)

        self.field_name = field_name
        self.current_value = current_value
        self.ai_value = ai_value
        self.confidence = confidence
        self.source_snippet = source_snippet
        self.on_accept = on_accept
        self.on_reject = on_reject

        self._build_ui()

    def _build_ui(self):
        confidence_color = self._get_confidence_color()

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))

        field_label = ctk.CTkLabel(header_frame, text=self.field_name, font=Theme.H3)
        field_label.pack(side="left")

        conf_label = ctk.CTkLabel(
            header_frame,
            text=f"Confidence: {self.confidence:.0%}",
            text_color=confidence_color,
            font=Theme.BODY,
        )
        conf_label.pack(side="right")

        if self.confidence < 0.85:
            warning_label = ctk.CTkLabel(
                header_frame,
                text="Low Confidence - Verify Manually",
                text_color=Theme.ERROR_RED,
                font=Theme.CAPTION,
            )
            warning_label.pack(side="right", padx=10)

        values_frame = ctk.CTkFrame(self, fg_color="transparent")
        values_frame.pack(fill="x", padx=10, pady=5)

        current_label = ctk.CTkLabel(
            values_frame, text="Current Value:", font=Theme.BODY
        )
        current_label.pack(side="left")

        current_value = ctk.CTkLabel(
            values_frame,
            text=str(self.current_value) if self.current_value is not None else "N/A",
            font=Theme.BODY_BOLD,
            text_color=Theme.TAX_AMBER,
        )
        current_value.pack(side="left", padx=5)

        arrow_label = ctk.CTkLabel(values_frame, text="  ->  ", font=Theme.BODY)
        arrow_label.pack(side="left")

        ai_value = ctk.CTkLabel(
            values_frame,
            text=str(self.ai_value) if self.ai_value is not None else "N/A",
            font=Theme.BODY_BOLD,
            text_color=Theme.SUCCESS_GREEN,
        )
        ai_value.pack(side="left", padx=5)

        if self.source_snippet:
            snippet_frame = ctk.CTkFrame(self, fg_color=Theme.BG_INPUT)
            snippet_frame.pack(fill="x", padx=10, pady=5)

            snippet_label = ctk.CTkLabel(
                snippet_frame,
                text=f"Source: {self.source_snippet[:100]}...",
                font=Theme.CAPTION,
                text_color=Theme.TEXT_MUTED,
                justify="left",
            )
            snippet_label.pack(anchor="w", padx=5, pady=5)

        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=10, pady=(5, 10))

        reject_btn = ctk.CTkButton(
            buttons_frame,
            text="Reject",
            width=100,
            command=self._on_reject,
            **Theme.get_button_style("danger"),
        )
        reject_btn.pack(side="right", padx=5)

        accept_btn = ctk.CTkButton(
            buttons_frame,
            text="Accept",
            width=100,
            command=self._on_accept,
            **Theme.get_button_style("emerald"),
        )
        accept_btn.pack(side="right", padx=5)

    def _get_confidence_color(self) -> str:
        if self.confidence >= 0.95:
            return Theme.SUCCESS_GREEN
        elif self.confidence >= 0.85:
            return Theme.TTI_PURPLE
        elif self.confidence >= 0.70:
            return Theme.WARNING
        else:
            return Theme.ERROR_RED

    def _on_accept(self):
        logger.info(f"Accepted AI suggestion for {self.field_name}: {self.ai_value}")

        log_audit_decision(
            field=self.field_name,
            ai_value=self.ai_value,
            final_value=self.ai_value,
            confidence=self.confidence,
            accepted=True,
        )

        if self.on_accept:
            self.on_accept(self.field_name, self.ai_value)

        self.destroy()

    def _on_reject(self):
        logger.info(f"Rejected AI suggestion for {self.field_name}")

        log_audit_decision(
            field=self.field_name,
            ai_value=self.ai_value,
            final_value=self.current_value,
            confidence=self.confidence,
            accepted=False,
        )

        if self.on_reject:
            self.on_reject(self.field_name)

        self.destroy()


class AIPanel(ctk.CTkFrame):

    def __init__(self, parent, root_window=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.root_window = root_window
        self.suggestions = []
        self.pending_callback = None

        self._build_ui()

    def _build_ui(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))

        title_label = ctk.CTkLabel(header_frame, text="AI Suggestions", font=Theme.H1)
        title_label.pack(side="left")

        self.count_label = ctk.CTkLabel(
            header_frame, text="0 pending", font=Theme.BODY, text_color=Theme.TEXT_MUTED
        )
        self.count_label.pack(side="right")

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.empty_label = ctk.CTkLabel(
            self.scroll_frame,
            text="No AI suggestions pending.\nImport a Form 16 to get started.",
            font=Theme.BODY_BOLD,
            text_color=Theme.TEXT_DIM,
        )
        self.empty_label.pack(pady=50)

        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(fill="x", padx=15, pady=(10, 15))

        accept_all_btn = ctk.CTkButton(
            actions_frame,
            text="Accept All High Confidence (>95%)",
            **Theme.get_button_style("primary"),
        )
        accept_all_btn.pack(side="left")

        clear_btn = ctk.CTkButton(
            actions_frame, text="Clear All", **Theme.get_button_style("secondary")
        )
        clear_btn.pack(side="right")

    def add_suggestion(
        self,
        field_name: str,
        current_value: Any,
        ai_value: Any,
        confidence: float,
        source_snippet: str = "",
    ):
        if self.empty_label:
            self.empty_label.pack_forget()

        suggestion = AISuggestionItem(
            self.scroll_frame,
            field_name=field_name,
            current_value=current_value,
            ai_value=ai_value,
            confidence=confidence,
            source_snippet=source_snippet,
            on_accept=self._on_suggestion_accepted,
            on_reject=self._on_suggestion_rejected,
            fg_color=Theme.BG_SECONDARY,
            border_color=Theme.SECTION_BORDER,
            border_width=1,
        )
        suggestion.pack(fill="x", pady=5)

        self.suggestions.append(suggestion)
        self._update_count()

    def _on_suggestion_accepted(self, field: str, value: Any):
        if self.pending_callback:
            self.pending_callback(field, value, "accept")

        self._remove_suggestion(field)

    def _on_suggestion_rejected(self, field: str):
        if self.pending_callback:
            self.pending_callback(field, None, "reject")

        self._remove_suggestion(field)

    def _remove_suggestion(self, field_name: str):
        self.suggestions = [s for s in self.suggestions if s.field_name != field_name]
        self._update_count()

        if not self.suggestions:
            self.empty_label.pack(pady=50)

    def _accept_all_high_confidence(self):
        accepted = []

        for suggestion in self.suggestions[:]:
            if suggestion.confidence >= 0.95:
                suggestion._on_accept()
                accepted.append(suggestion.field_name)

        logger.info(f"Accepted {len(accepted)} high confidence suggestions")

    def _clear_all(self):
        for suggestion in self.suggestions[:]:
            suggestion.destroy()

        self.suggestions = []
        self._update_count()
        self.empty_label.pack(pady=50)

    def _update_count(self):
        count = len(self.suggestions)
        self.count_label.configure(text=f"{count} pending")

    def set_callback(self, callback: Callable):
        self.pending_callback = callback

    def get_pending_count(self) -> int:
        return len(self.suggestions)

    def is_empty(self) -> bool:
        return len(self.suggestions) == 0


def show_ai_panel(_root, vardict: dict, ai_result: dict, callback: Callable):
    if not CTK_AVAILABLE:
        logger.error("CustomTkinter not available")
        return

    ai_data = ai_result.get("data", {})
    if not ai_data:
        logger.warning("No AI data to display")
        return

    confidence = ai_data.get("confidence", 0)

    suggestions = []

    field_mappings = {
        "sal_gross": ("Gross Salary", "sal_gross"),
        "sal_perks": ("Perquisites", "sal_perks"),
        "ded_16ia": ("Standard Deduction", "ded_16ia"),
    }

    for field_key, (display_name, vardict_key) in field_mappings.items():
        if field_key in ai_data and ai_data[field_key] is not None:
            current_value = vardict.get(vardict_key)
            ai_value = ai_data[field_key]

            suggestions.append(
                {
                    "field": display_name,
                    "field_key": vardict_key,
                    "current": current_value,
                    "ai": ai_value,
                    "confidence": confidence,
                }
            )

    return suggestions


def create_ai_toggle_frame(parent) -> ctk.CTkFrame:
    frame = ctk.CTkFrame(parent)

    label = ctk.CTkLabel(frame, text="AI Assistant", font=Theme.H3)
    label.pack(side="left", padx=10)

    ai_manager = get_ai_manager()
    is_enabled = ai_manager.is_enabled()

    toggle = ctk.CTkSwitch(
        frame,
        text="Enable AI Extraction",
        onvalue=True,
        offvalue=False,
        command=lambda: _toggle_ai(toggle.get()),
    )
    toggle.select() if is_enabled else toggle.deselect()
    toggle.pack(side="left", padx=10)

    profile_label = ctk.CTkLabel(
        frame,
        text=f"Profile: {ai_manager.get_profile().upper()}",
        font=Theme.BODY,
        text_color=Theme.TEXT_MUTED,
    )
    profile_label.pack(side="right", padx=10)

    return frame


def _toggle_ai(enabled: bool):
    logger.info(f"AI toggled: {enabled}")
    from src.services.settings_service import SettingsManager

    try:
        SettingsManager.set("AI.enabled", enabled)
        logger.info(f"AI {'enabled' if enabled else 'disabled'} in settings")
    except Exception as e:
        logger.error(f"Failed to update AI settings: {e}")
