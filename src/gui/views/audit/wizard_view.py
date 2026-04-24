from src.gui.styles.constants import SPACING_SM, SPACING_LG, INNER_PADX, BUTTON_HEIGHT_SM
import customtkinter as ctk
from src.gui.styles.theme import Theme
from src.gui.widgets.common import page_header, make_card


class WizardSchedule:
    @staticmethod
    def create_frame(parent, fv, on_complete):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        page_header(
            f,
            "ITR SELECTION WIZARD",
            "Answer a few questions to determine your correct ITR form.",
        )

        q_card = make_card(f, "QUICK PROFILE ASSESSMENT")

        q_vars = {
            "inc_gt_50l": ctk.StringVar(value="No"),
            "has_bp": ctk.StringVar(value="No"),
            "is_director": ctk.StringVar(value="No"),
            "has_unlisted": ctk.StringVar(value="No"),
            "has_foreign": ctk.StringVar(value="No"),
            "has_agri_gt_5k": ctk.StringVar(value="No"),
            "has_vda": ctk.StringVar(value="No"),
            "has_taxable_cg": ctk.StringVar(value="No"),
            "hp_gt_2": ctk.StringVar(value="No"),
        }

        def _q_row(lbl, var):
            row = ctk.CTkFrame(q_card, fg_color="transparent")
            row.pack(fill="x", padx=INNER_PADX, pady=SPACING_SM)
            row.grid_columnconfigure(0, weight=1)
            row.grid_columnconfigure(1, minsize=140)

            label_widget = ctk.CTkLabel(
                row, text=lbl, font=Theme.BODY, text_color=Theme.TEXT_DIM, anchor="w", justify="left"
            )
            label_widget.grid(row=0, column=0, sticky="ew", padx=INNER_PADX)

            ctk.CTkSegmentedButton(
                row,
                values=["No", "Yes"],
                variable=var,
                selected_color=Theme.ACCENT_PRIMARY,
                height=BUTTON_HEIGHT_SM,
            ).grid(row=0, column=1, sticky="e", padx=INNER_PADX)

        _q_row("1. Is your total income > ₹50 Lakhs?", q_vars["inc_gt_50l"])
        _q_row("2. Do you have Business or Profession income?", q_vars["has_bp"])
        _q_row("3. Are you a Director in any company?", q_vars["is_director"])
        _q_row("4. Do you hold unlisted equity shares?", q_vars["has_unlisted"])
        _q_row("5. Do you have any Foreign Assets/Income?", q_vars["has_foreign"])
        _q_row("6. Is your Agricultural Income > ₹5,000?", q_vars["has_agri_gt_5k"])
        _q_row("7. Do you have VDA (Crypto) income?", q_vars["has_vda"])
        _q_row("8. Do you have taxable Capital Gains (beyond 112A exemption)?",
               q_vars["has_taxable_cg"])
        _q_row("9. Do you own more than 2 House Properties?", q_vars["hp_gt_2"])

        def calculate_itr():
            res = "ITR-1"
            config = {
                "has_salary": True,
                "has_house_property": True,
                "has_business": q_vars["has_bp"].get() == "Yes",
                "has_capital_gains": q_vars["has_unlisted"].get() == "Yes",
                "has_other_sources": True,
                "has_vda": q_vars["has_vda"].get() == "Yes",
            }

            if q_vars["has_bp"].get() == "Yes":
                res = "ITR-4"
                config["has_business"] = True

            is_complex = any(
                q_vars[k].get() == "Yes"
                for k in [
                    "inc_gt_50l",
                    "is_director",
                    "has_unlisted",
                    "has_foreign",
                    "has_agri_gt_5k",
                    "has_vda",
                    "has_taxable_cg",
                    "hp_gt_2",
                ]
            )

            if is_complex:
                if q_vars["has_bp"].get() == "Yes":
                    res = "ITR-3"
                else:
                    res = "ITR-2"
                config["has_capital_gains"] = True

            config["itr_type"] = res
            on_complete(config)

        ctk.CTkButton(
            f,
            text="APPLY SUGGESTED PROFILE & FORM",
            command=calculate_itr,
            **Theme.get_button_style("primary")
        ).pack(pady=SPACING_LG)

        return f
