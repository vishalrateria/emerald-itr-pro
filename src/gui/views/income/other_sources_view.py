import customtkinter as ctk
from src.gui.styles.theme import Theme
from src.gui.widgets.common import (
    page_header,
    make_card,
    card_spacer,
    field_row,
    total_row,
)


class OtherSourcesSchedule:
    @staticmethod
    def create_frame(parent, form_vars, sl, validation_refs=None, itr_type="ITR-4"):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        page_header(
            f,
            "SCHEDULE OS — OTHER SOURCES",
            "Income chargeable under 'Income from Other Sources'",
            accent_color=Theme.GTI_BLUE
        )
        int_card = make_card(f, "INTEREST INCOME", accent_color=Theme.GTI_BLUE)
        field_row(
            int_card,
            "Savings Bank Interest",
            form_vars["os_interest"],
            key="os_interest",
            validation_refs=validation_refs,
        )
        field_row(
            int_card,
            "IT Refund Interest",
            form_vars["os_interest_it"],
            key="os_interest_it",
            validation_refs=validation_refs,
        )
        field_row(
            int_card,
            "Other Interest",
            form_vars["os_interest_other"],
            key="os_interest_other",
            validation_refs=validation_refs,
        )
        field_row(
            int_card,
            "Concessional Int. u/s 194LC",
            form_vars["os_interest_concessional"],
            key="os_interest_concessional",
            validation_refs=validation_refs,
        )
        card_spacer(int_card)
        div_card = make_card(f, "DIVIDEND INCOME")
        field_row(
            div_card,
            "Dividend — Indian Companies",
            form_vars["os_dividend"],
            key="os_dividend",
            validation_refs=validation_refs,
        )
        field_row(
            div_card,
            "Dividend — Foreign Companies",
            form_vars["os_dividend_foreign"],
            key="os_dividend_foreign",
            validation_refs=validation_refs,
        )
        field_row(
            div_card,
            "Buyback Proceeds (Taxed as Dividend)",
            form_vars["buyback_price"],
            key="buyback_price",
            validation_refs=validation_refs,
        )
        card_spacer(div_card)
        misc_card = make_card(f, "MISCELLANEOUS")
        field_row(
            misc_card,
            "Family Pension Received",
            form_vars["os_pension"],
            key="os_pension",
            validation_refs=validation_refs,
        )
        field_row(
            misc_card,
            "Less: Standard Ded. (Lower of 1/3 or ₹25k)",
            form_vars["os_family_pension_ded"],
            state="readonly",
        )
        field_row(
            misc_card,
            "Winnings (Lottery, Online Gaming, etc.)",
            form_vars["os_winnings"],
            key="os_winnings",
            validation_refs=validation_refs,
        )
        field_row(
            misc_card,
            "Gift Income (Aggregate from Non-Relatives)",
            form_vars["os_gift"],
            key="os_gift",
            validation_refs=validation_refs,
        )
        field_row(
            misc_card,
            "Any Other Income",
            form_vars["os_other"],
            key="os_other",
            validation_refs=validation_refs,
        )
        card_spacer(misc_card)

        if itr_type not in ["ITR-1", "ITR-4"]:
            relief_card = make_card(f, "STATUTORY RELIEF (SEC 89A)")
            field_row(
                relief_card,
                "Relief u/s 89A (Foreign Retirement Fund)",
                form_vars["has_89a_relief"],
                key="has_89a_relief",
                validation_refs=validation_refs,
            )
            card_spacer(relief_card)

        tot_card = make_card(f, pady_bottom=16)
        total_row(
            tot_card,
            "TOTAL INCOME FROM OTHER SOURCES",
            "os_total",
            sl,
            color=Theme.SUCCESS_GREEN,
        )
        return f
