import customtkinter as ctk
from src.gui.styles.theme import Theme
from src.gui.widgets.common import (
    page_header,
    make_card,
    card_spacer,
    field_row,
)

class SalarySchedule:
    @staticmethod
    def create_frame(
        parent: ctk.CTkFrame,
        form_vars: dict,
        validation_refs: dict = None
    ) -> ctk.CTkFrame:
        f = ctk.CTkFrame(parent, fg_color="transparent")
        page_header(
            f,
            "SALARY INCOME & DEDUCTIONS",
            "Schedule S — Sections 17(1), 17(2), 17(3)  |  New Tax Regime",
            accent_color=Theme.GTI_BLUE
        )
        gross = make_card(f, "GROSS SALARY COMPONENTS", accent_color=Theme.GTI_BLUE)
        field_row(
            gross,
            "1a. Salary  u/s 17(1)",
            form_vars["sal_gross"],
            key="sal_gross",
            validation_refs=validation_refs,
            tooltip="Basic salary, dearness allowance, and bonus as per Form 16 Part B."
        )
        field_row(
            gross,
            "1b. Perquisites  u/s 17(2)",
            form_vars["sal_perks"],
            key="sal_perks",
            validation_refs=validation_refs,
            tooltip="Value of rent-free accommodation, car, etc., provided by employer."
        )
        field_row(
            gross,
            "1c. Profits in lieu of salary u/s 17(3)",
            form_vars["sal_profits"],
            key="sal_profits",
            validation_refs=validation_refs,
            tooltip="Retrenchment compensation or payments from unrecognised provident fund."
        )
        card_spacer(gross)
        allow = make_card(f, "EXEMPT ALLOWANCES")
        field_row(allow, "2. Exempt Allowances u/s 10", form_vars["sal_allowance"])
        card_spacer(allow)
        ded = make_card(f, "DEDUCTIONS  u/s 16")
        field_row(
            ded,
            "3a. Standard Deduction  u/s 16(ia)",
            form_vars["sal_std_ded"],
            variant="calc",
            state="readonly",
        )
        card_spacer(ded)
        net = make_card(f, "NET SALARY INCOME", title_color=Theme.SUCCESS_GREEN)
        field_row(
            net,
            "Net Salary (after deductions u/s 16)",
            form_vars["sal"],
            variant="total",
            state="readonly",
        )
        card_spacer(net)
        return f
