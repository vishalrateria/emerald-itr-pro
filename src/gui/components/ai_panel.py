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


class AISuggestionItem(ctk.CTkFrame):
    """Single AI suggestion item with accept/reject buttons."""
    
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
        **kwargs
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
        
        field_label = ctk.CTkLabel(
            header_frame,
            text=self.field_name,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        field_label.pack(side="left")
        
        conf_label = ctk.CTkLabel(
            header_frame,
            text=f"Confidence: {self.confidence:.0%}",
            text_color=confidence_color,
            font=ctk.CTkFont(size=12)
        )
        conf_label.pack(side="right")
        
        if self.confidence < 0.85:
            warning_label = ctk.CTkLabel(
                header_frame,
                text="Low Confidence - Verify Manually",
                text_color="#FF6B6B",
                font=ctk.CTkFont(size=10)
            )
            warning_label.pack(side="right", padx=10)
        
        values_frame = ctk.CTkFrame(self, fg_color="transparent")
        values_frame.pack(fill="x", padx=10, pady=5)
        
        current_label = ctk.CTkLabel(
            values_frame,
            text="Current Value:",
            font=ctk.CTkFont(size=12)
        )
        current_label.pack(side="left")
        
        current_value = ctk.CTkLabel(
            values_frame,
            text=str(self.current_value) if self.current_value is not None else "N/A",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#FFA500"
        )
        current_value.pack(side="left", padx=5)
        
        arrow_label = ctk.CTkLabel(
            values_frame,
            text="  ->  ",
            font=ctk.CTkFont(size=12)
        )
        arrow_label.pack(side="left")
        
        ai_value = ctk.CTkLabel(
            values_frame,
            text=str(self.ai_value) if self.ai_value is not None else "N/A",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#4CAF50"
        )
        ai_value.pack(side="left", padx=5)
        
        if self.source_snippet:
            snippet_frame = ctk.CTkFrame(self, fg_color="#2B2B2B")
            snippet_frame.pack(fill="x", padx=10, pady=5)
            
            snippet_label = ctk.CTkLabel(
                snippet_frame,
                text=f"Source: {self.source_snippet[:100]}...",
                font=ctk.CTkFont(size=10),
                text_color="#888888",
                justify="left"
            )
            snippet_label.pack(anchor="w", padx=5, pady=5)
        
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        reject_btn = ctk.CTkButton(
            buttons_frame,
            text="Reject",
            fg_color="#FF4444",
            hover_color="#CC0000",
            width=100,
            command=self._on_reject
        )
        reject_btn.pack(side="right", padx=5)
        
        accept_btn = ctk.CTkButton(
            buttons_frame,
            text="Accept",
            fg_color="#4CAF50",
            hover_color="#388E3C",
            width=100,
            command=self._on_accept
        )
        accept_btn.pack(side="right", padx=5)
    
    def _get_confidence_color(self) -> str:
        if self.confidence >= 0.95:
            return "#4CAF50"
        elif self.confidence >= 0.85:
            return "#8BC34A"
        elif self.confidence >= 0.70:
            return "#FFC107"
        else:
            return "#FF5722"
    
    def _on_accept(self):
        logger.info(f"Accepted AI suggestion for {self.field_name}: {self.ai_value}")
        
        log_audit_decision(
            field=self.field_name,
            ai_value=self.ai_value,
            final_value=self.ai_value,
            confidence=self.confidence,
            accepted=True
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
            accepted=False
        )
        
        if self.on_reject:
            self.on_reject(self.field_name)
        
        self.destroy()


class AIPanel(ctk.CTkFrame):
    """
    AI Verification Queue Panel.
    
    Displays side-by-side comparison of Current Value vs AI Suggested Value.
    Allows user to Accept or Reject each suggestion.
    """
    
    def __init__(self, parent, root_window=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.root_window = root_window
        self.suggestions = []
        self.pending_callback = None
        
        self._build_ui()
    
    def _build_ui(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="AI Suggestions",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(side="left")
        
        self.count_label = ctk.CTkLabel(
            header_frame,
            text="0 pending",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.count_label.pack(side="right")
        
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.empty_label = ctk.CTkLabel(
            self.scroll_frame,
            text="No AI suggestions pending.\nImport a Form 16 to get started.",
            font=ctk.CTkFont(size=14),
            text_color="#666666"
        )
        self.empty_label.pack(pady=50)
        
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(fill="x", padx=15, pady=(10, 15))
        
        accept_all_btn = ctk.CTkButton(
            actions_frame,
            text="Accept All High Confidence (>95%)",
            fg_color="#2196F3",
            hover_color="#1976D2",
            command=self._accept_all_high_confidence
        )
        accept_all_btn.pack(side="left")
        
        clear_btn = ctk.CTkButton(
            actions_frame,
            text="Clear All",
            fg_color="#666666",
            hover_color="#444444",
            command=self._clear_all
        )
        clear_btn.pack(side="right")
    
    def add_suggestion(
        self,
        field_name: str,
        current_value: Any,
        ai_value: Any,
        confidence: float,
        source_snippet: str = ""
    ):
        """Add a new AI suggestion to the queue."""
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
            fg_color="#1E1E1E",
            border_color="#333333",
            border_width=1
        )
        suggestion.pack(fill="x", pady=5)
        
        self.suggestions.append(suggestion)
        self._update_count()
    
    def _on_suggestion_accepted(self, field: str, value: Any):
        """Handle suggestion accepted."""
        if self.pending_callback:
            self.pending_callback(field, value, "accept")
        
        self._remove_suggestion(field)
    
    def _on_suggestion_rejected(self, field: str):
        """Handle suggestion rejected."""
        if self.pending_callback:
            self.pending_callback(field, None, "reject")
        
        self._remove_suggestion(field)
    
    def _remove_suggestion(self, field_name: str):
        """Remove suggestion by field name."""
        self.suggestions = [s for s in self.suggestions if s.field_name != field_name]
        self._update_count()
        
        if not self.suggestions:
            self.empty_label.pack(pady=50)
    
    def _accept_all_high_confidence(self):
        """Accept all suggestions with confidence > 95%."""
        accepted = []
        
        for suggestion in self.suggestions[:]:
            if suggestion.confidence >= 0.95:
                suggestion._on_accept()
                accepted.append(suggestion.field_name)
        
        logger.info(f"Accepted {len(accepted)} high confidence suggestions")
    
    def _clear_all(self):
        """Clear all pending suggestions."""
        for suggestion in self.suggestions[:]:
            suggestion.destroy()
        
        self.suggestions = []
        self._update_count()
        self.empty_label.pack(pady=50)
    
    def _update_count(self):
        """Update the pending count label."""
        count = len(self.suggestions)
        self.count_label.configure(text=f"{count} pending")
    
    def set_callback(self, callback: Callable):
        """Set callback for accept/reject actions."""
        self.pending_callback = callback
    
    def get_pending_count(self) -> int:
        """Get number of pending suggestions."""
        return len(self.suggestions)
    
    def is_empty(self) -> bool:
        """Check if panel has no suggestions."""
        return len(self.suggestions) == 0


def show_ai_panel(root, vardict: dict, ai_result: dict, callback: Callable):
    """
    Show AI verification panel with results.
    
    Args:
        root: Root window
        vardict: Current VarDict state
        ai_result: AI extraction result
        callback: Function(field, value, action) called on accept/reject
    """
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
            
            suggestions.append({
                "field": display_name,
                "field_key": vardict_key,
                "current": current_value,
                "ai": ai_value,
                "confidence": confidence
            })
    
    return suggestions


def create_ai_toggle_frame(parent) -> ctk.CTkFrame:
    """
    Create AI toggle frame for settings.
    
    Returns a frame with AI enable/disable toggle.
    """
    frame = ctk.CTkFrame(parent)
    
    label = ctk.CTkLabel(
        frame,
        text="AI Assistant",
        font=ctk.CTkFont(size=14, weight="bold")
    )
    label.pack(side="left", padx=10)
    
    ai_manager = get_ai_manager()
    is_enabled = ai_manager.is_enabled()
    
    toggle = ctk.CTkSwitch(
        frame,
        text="Enable AI Extraction",
        onvalue=True,
        offvalue=False,
        command=lambda: _toggle_ai(toggle.get())
    )
    toggle.select() if is_enabled else toggle.deselect()
    toggle.pack(side="left", padx=10)
    
    profile_label = ctk.CTkLabel(
        frame,
        text=f"Profile: {ai_manager.get_profile().upper()}",
        font=ctk.CTkFont(size=12),
        text_color="#888888"
    )
    profile_label.pack(side="right", padx=10)
    
    return frame


def _toggle_ai(enabled: bool):
    """Handle AI toggle change."""
    logger.info(f"AI toggled: {enabled}")
    
    settings_path = "settings.json"
    try:
        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                settings = json.load(f)
        else:
            settings = {}
        
        settings["ai_enabled"] = enabled
        
        with open(settings_path, "w") as f:
            json.dump(settings, f, indent=2)
        
        logger.info(f"AI {'enabled' if enabled else 'disabled'} in settings")
    except Exception as e:
        logger.error(f"Failed to update AI settings: {e}")
