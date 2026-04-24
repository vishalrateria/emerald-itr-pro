from src.gui.styles.constants import SPACING_XS, SPACING_SM, SPACING_MD
from src.gui.styles.theme import Theme
from src.services.logging_service import log as logger


class NavigatorMixin:
    def go_to_step(self, idx):
        if idx < 0 or idx >= len(self.steps):
            return
        if not self.step_visibility.get(self.steps[idx]["id"], True):
            return
        self.welcome_frame.pack_forget()
        for b_tuple in self.step_buttons.values():
            b_tuple[0].configure(state="normal")
        self.footer.grid(row=1, column=0, sticky="ew")
        self.current_step_idx = idx
        step_id = self.steps[idx]["id"]
        if not hasattr(self, "visited_steps"):
            self.visited_steps = set()
        self.visited_steps.add(step_id)
        self.update_wizard_steps()
        for i, (btn, indicator, row) in self.step_buttons.items():
            if i == idx:
                btn.configure(fg_color=Theme.BG_INPUT, text_color=Theme.ACCENT_PRIMARY, font=Theme.BODY_BOLD)
                indicator.configure(fg_color=Theme.ACCENT_PRIMARY)
            else:
                btn.configure(fg_color="transparent", text_color=Theme.TEXT_DIM, font=Theme.BODY)
                indicator.configure(fg_color="transparent")
        for f in self.frames.values():
            try:
                f.pack_forget()
            except Exception as e:
                logger.debug(f"Frame hide error: {e}")
        current_step = self.steps[idx]
        for f_key in current_step["frames"]:
            f = self.get_or_create_frame(f_key)
            if f:
                f.pack(fill="x", pady=(0, SPACING_MD))
        try:
            self.scrollable_content._parent_canvas.yview_moveto(0)
        except Exception as e:
            logger.debug(f"Scroll reset error: {e}")

    def go_to_step_by_id(self, step_id):
        for i, step in enumerate(self.steps):
            if step["id"] == step_id:
                self.go_to_step(i)
                return

    def next_step(self):
        idx = self.current_step_idx + 1
        while idx < len(self.steps) and not self.step_visibility.get(self.steps[idx]["id"], True):
            idx += 1
        if idx < len(self.steps):
            self.go_to_step(idx)

    def prev_step(self):
        idx = self.current_step_idx - 1
        while idx >= 0 and not self.step_visibility.get(self.steps[idx]["id"], True):
            idx -= 1
        if idx >= 0:
            self.go_to_step(idx)

    def update_wizard_steps(self):
        config = self.profile_configurator.get_profile_config() if self.profile_configurator else {}
        self.step_visibility = {
            "setup": True, "personal": True,
            "income_salary": config.get("has_salary", True),
            "income_hp": config.get("has_house_property", True),
            "income_bp": config.get("has_business", True),
            "income_cg": config.get("has_capital_gains", True),
            "income_os": config.get("has_other_sources", True),
            "foreign_assets": config.get("has_foreign_assets", False),
            "deductions": True, "taxes": True, "review": True, "verify": True, "tools": True,
        }
        visible_idx = 1
        for idx, step in enumerate(self.steps):
            if idx in self.step_buttons:
                btn, indicator, row = self.step_buttons[idx]
                if self.step_visibility.get(step["id"], True):
                    is_visited = hasattr(self, "visited_steps") and step["id"] in self.visited_steps
                    status_prefix = "✓ " if is_visited else f"{visible_idx}. "
                    btn.configure(text=status_prefix + step["title"])
                    row.pack(fill="x", side="top", pady=1)
                    visible_idx += 1
                else:
                    row.pack_forget()
