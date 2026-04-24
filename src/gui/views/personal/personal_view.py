from src.gui.styles.constants import SPACING_SM, SPACING_MD, INNER_PADX, BUTTON_HEIGHT
import customtkinter as ctk
from src.gui.styles.theme import Theme
from src.gui.widgets.common import (
    page_header,
    make_card,
    card_spacer,
    field_row,
    combo_field_row,
)

class PersonalSchedule:
    @staticmethod
    def create_frame(
        parent: ctk.CTkFrame,
        form_vars: dict,
        dynamic_refs: dict = None,
        validation_refs: dict = None
    ) -> ctk.CTkFrame:
        f = ctk.CTkFrame(parent, fg_color="transparent")
        page_header(
            f,
            "PERSONAL IDENTITY & FILING STATUS",
            "Assessee details — AY 2026-27",
            accent_color=Theme.BRAND_BLUE
        )
        id_card = make_card(f, "IDENTITY", accent_color=Theme.BRAND_BLUE)
        from src.services.io.import_service import ImportService
        import_row = ctk.CTkFrame(id_card, fg_color="transparent")
        import_row.pack(fill="x", padx=INNER_PADX, pady=(SPACING_SM, SPACING_SM))
        ctk.CTkButton(
            import_row,
            text="🧬 IMPORT PRE-FILL",
            command=lambda: ImportService.import_prefill(form_vars),
            height=BUTTON_HEIGHT,
            font=Theme.BODY_BOLD,
            **Theme.get_button_style("primary")
        ).pack(side="left", padx=SPACING_SM)
        ctk.CTkButton(
            import_row,
            text="📊 IMPORT AIS/TIS",
            command=lambda: ImportService.import_ais_json(form_vars),
            height=BUTTON_HEIGHT,
            font=Theme.BODY_BOLD,
            **Theme.get_button_style("primary")
        ).pack(side="left", padx=SPACING_SM)
        ctk.CTkButton(
            import_row,
            text="IMPORT FORM 16 (AI)",
            command=lambda: _handle_form16_import(parent, form_vars),
            height=BUTTON_HEIGHT,
            font=Theme.BODY_BOLD,
            **Theme.get_button_style("primary")
        ).pack(side="left", padx=SPACING_SM)
        ctk.CTkButton(
            import_row,
            text="FORM 26AS (AI)",
            command=lambda: _handle_form26as_import(parent, form_vars),
            height=BUTTON_HEIGHT,
            font=Theme.BODY_BOLD,
            **Theme.get_button_style("secondary")
        ).pack(side="left", padx=SPACING_SM)
        ctk.CTkButton(
            import_row,
            text="AIS JSON (AI)",
            command=lambda: _handle_ais_ai_import(parent, form_vars),
            height=BUTTON_HEIGHT,
            font=Theme.BODY_BOLD,
            **Theme.get_button_style("secondary")
        ).pack(side="left", padx=SPACING_SM)
        ctk.CTkButton(
            import_row,
            text="TAX ADVISOR (AI)",
            command=lambda: _handle_tax_advisory(parent, form_vars),
            height=BUTTON_HEIGHT,
            font=Theme.BODY_BOLD,
            **Theme.get_button_style("accent")
        ).pack(side="left", padx=SPACING_SM)
        field_row(
            id_card,
            "PAN Number",
            form_vars["pan"],
            key="pan",
            validation_refs=validation_refs,
            tooltip="10-digit Alphanumeric ID. Must be in format: ABCDE1234F"
        )
        field_row(
            id_card,
            "Aadhaar Number (12 digits)",
            form_vars["aadhaar"],
            key="aadhaar",
            validation_refs=validation_refs,
            tooltip="12-digit UIDAI Number"
        )
        field_row(
            id_card,
            "Full Name",
            form_vars["name"],
            key="name",
            validation_refs=validation_refs,
        )
        field_row(
            id_card,
            "Date of Birth (DD-MM-YYYY)",
            form_vars["dob"],
            key="dob",
            validation_refs=validation_refs,
            tooltip="Enter date in DD-MM-YYYY format"
        )
        field_row(
            id_card,
            "Email Address",
            form_vars["email"],
            key="email",
            validation_refs=validation_refs,
        )
        field_row(
            id_card,
            "Mobile Number",
            form_vars["mobile"],
            key="mobile",
            validation_refs=validation_refs,
        )
        field_row(
            id_card,
            "Passport Number (For Non-Residents)",
            form_vars["passport"],
            key="passport",
            validation_refs=validation_refs,
        )
        field_row(id_card, "Secondary Email (Optional)", form_vars["email2"])
        field_row(id_card, "Secondary Mobile (Optional)", form_vars["mobile2"])
        combo_field_row(
            id_card,
            "Aadhaar-PAN Link Status",
            form_vars["aadhaar_link_status"],
            ["Linked", "NotLinked", "Pending", "Invalid"],
        )
        card_spacer(id_card)
        fs_card = make_card(f, "FILING STATUS")
        combo_field_row(
            fs_card,
            "Residential Status",
            form_vars["filing_status"],
            ["Resident", "Non-Resident", "RNOR"],
        )
        combo_field_row(
            fs_card,
            "Taxpayer Status",
            form_vars["status"],
            ["Individual", "HUF", "Firm", "LLP"],
        )
        combo_field_row(
            fs_card,
            "Employer Category",
            form_vars["emp_cat"],
            ["Government", "Private", "Pensioner", "Others"],
        )
        combo_field_row(
            fs_card,
            "Filed by Representative Assessee",
            form_vars["rep_assessee"],
            ["No", "Yes"],
        )
        combo_field_row(
            fs_card,
            "Revised Return filed after Dec 31st?",
            form_vars["is_revised_after_dec31"],
            ["No", "Yes"],
        )
        field_row(
            fs_card,
            "Actual Return Filing Date (DD-MM-YYYY)",
            form_vars["return_filing_date"],
        )
        field_row(
            fs_card, "Months Delayed for 234B (from April 1)", form_vars["months_234b"]
        )
        ctk.CTkFrame(f, height=SPACING_MD, fg_color="transparent").pack()
        cg_card = make_card(f, "CAPITAL GAINS QUARTERLY BREAKUP (For 234C Relaxation)")
        field_row(cg_card, "Apr 1 to Jun 15 ₹", form_vars["cg_q1_jun15"])
        field_row(cg_card, "Jun 16 to Sep 15 ₹", form_vars["cg_q2_sep15"])
        field_row(cg_card, "Sep 16 to Dec 15 ₹", form_vars["cg_q3_dec15"])
        field_row(cg_card, "Dec 16 to Mar 15 ₹", form_vars["cg_q4_mar15"])
        field_row(cg_card, "Mar 16 to Mar 31 ₹", form_vars["cg_q5_mar31"])
        rep_card = make_card(
            f, "REPRESENTATIVE ASSESSEE DETAILS (MANDATORY if toggle is Yes)"
        )
        field_row(rep_card, "Representative Name", form_vars["rep_name"])
        field_row(rep_card, "Representative Email", form_vars["rep_email"])
        field_row(rep_card, "Representative Mobile", form_vars["rep_mobile"])
        if dynamic_refs is not None:
            dynamic_refs["rep_card"] = rep_card
        card_spacer(rep_card)
        ctk.CTkFrame(f, height=SPACING_MD, fg_color="transparent").pack()
        p_addr_card = make_card(f, "PRIMARY ADDRESS  (MANDATORY)")
        field_row(p_addr_card, "Flat/Door/Block No", form_vars["addr_flat"])
        field_row(p_addr_card, "Road/Street/Post Office", form_vars["addr_road"])
        field_row(p_addr_card, "Area/Locality", form_vars["addr_area"])
        field_row(p_addr_card, "City/Town/District", form_vars["addr_city"])
        states = [
            "Andhra", "Arunachal", "Assam", "Bihar", "Chhattisgarh", "Delhi", "Goa", "Gujarat", "Haryana",
            "Himachal", "J&K", "Jharkhand", "Karnataka", "Kerala", "MP", "Maharashtra", "Manipur", "Meghalaya",
            "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana",
            "Tripura", "UP", "Uttarakhand", "West Bengal", "Andaman", "Chandigarh", "Dadra", "Ladakh",
            "Lakshadweep", "Puducherry",
        ]
        combo_field_row(
            p_addr_card, "State / UT", form_vars["addr_state"], sorted(states)
        )
        field_row(p_addr_card, "Pin Code", form_vars["addr_pin"])
        ctk.CTkFrame(f, height=SPACING_MD, fg_color="transparent").pack()
        s_addr_card = make_card(f, "SECONDARY ADDRESS  (RECOMMENDED for AY 2026-27)")
        field_row(s_addr_card, "Flat/Door/Block No", form_vars["addr2_flat"])
        field_row(s_addr_card, "Road/Street/Post Office", form_vars["addr2_road"])
        field_row(s_addr_card, "Area/Locality", form_vars["addr2_area"])
        field_row(s_addr_card, "City/Town/District", form_vars["addr2_city"])
        combo_field_row(
            s_addr_card, "State / UT", form_vars["addr2_state"], sorted(states)
        )
        field_row(s_addr_card, "Pin Code", form_vars["addr2_pin"])
        if dynamic_refs is not None:
            dynamic_refs["addr2_card"] = s_addr_card
        card_spacer(s_addr_card)
        ver_card = make_card(f, "VERIFICATION & DECLARATION")
        field_row(
            ver_card, "Verification Place (Mandatory)", form_vars["verification_place"]
        )
        combo_field_row(
            ver_card,
            "Capacity",
            form_vars["capacity"],
            ["Self", "Representative", "HUF Karta"],
        )
        card_spacer(ver_card)
        return f


def _handle_form16_import(parent, form_vars):
    """Handle Form 16 PDF import with AI extraction."""
    from tkinter import filedialog, messagebox
    from src.services.io.import_service import ImportService

    try:
        import pypdf
    except ImportError:
        messagebox.showerror("Error", "pypdf not installed. Run: pip install pypdf")
        return

    path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
    if not path:
        return

    try:
        with open(path, "rb") as f:
            reader = pypdf.PdfReader(f)
            text = "\n".join(p.extract_text() for p in reader.pages)

        if not text.strip():
            messagebox.showwarning("Warning", "No text found in PDF")
            return

        root_window = parent.winfo_toplevel()

        def on_ai_result(result):
            if result.get("status") == "success":
                ai_data = result.get("data", {})
                _apply_ai_suggestions(form_vars, ai_data)
                messagebox.showinfo(
                    "AI Extraction Complete",
                    f"Extracted data from Form 16.\nConfidence: {ai_data.get('confidence', 0):.0%}\n\nReview and accept the suggestions."
                )
            elif result.get("status") == "disabled":
                messagebox.showwarning("AI Disabled", "AI is disabled. Enable it in Settings to use this feature.")
            else:
                messagebox.showerror("AI Error", result.get("error", "Unknown error"))

        ImportService.extract_with_ai(
            text=text,
            root_window=root_window,
            on_result=on_ai_result
        )

    except Exception as e:
        messagebox.showerror("Error", f"Failed to import Form 16: {e}")


def _handle_form26as_import(parent, form_vars):
    """Handle Form 26AS PDF import with AI extraction."""
    from tkinter import filedialog, messagebox
    from src.services.io.import_service import ImportService

    try:
        import pypdf
    except ImportError:
        messagebox.showerror("Error", "pypdf not installed. Run: pip install pypdf")
        return

    path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
    if not path:
        return

    try:
        with open(path, "rb") as f:
            reader = pypdf.PdfReader(f)
            text = "\n".join(p.extract_text() for p in reader.pages)

        if not text.strip():
            messagebox.showwarning("Warning", "No text found in PDF")
            return

        root_window = parent.winfo_toplevel()

        def on_ai_result(result):
            if result.get("status") == "success":
                ai_data = result.get("data", {})
                messagebox.showinfo(
                    "AI Form 26AS Extraction Complete",
                    f"Extracted TDS details.\nTotal TDS: Rs.{ai_data.get('total_tds', 0):,}\nConfidence: {ai_data.get('confidence', 0):.0%}"
                )
            elif result.get("status") == "disabled":
                messagebox.showwarning("AI Disabled", "AI is disabled. Enable it in Settings.")
            else:
                messagebox.showerror("AI Error", result.get("error", "Unknown error"))

        ImportService.extract_form26as_with_ai(
            text=text,
            root_window=root_window,
            on_result=on_ai_result
        )

    except Exception as e:
        messagebox.showerror("Error", f"Failed to import Form 26AS: {e}")


def _handle_ais_ai_import(parent, form_vars):
    """Handle AIS JSON import with AI extraction."""
    from tkinter import filedialog, messagebox, simpledialog
    from src.services.io.import_service import ImportService
    import json

    path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
    if not path:
        return

    try:
        with open(path, "r", encoding="utf-8") as f:
            ais_data = json.load(f)

        ais_json = json.dumps(ais_data)
        root_window = parent.winfo_toplevel()

        def on_ai_result(result):
            if result.get("status") == "success":
                ai_data = result.get("data", {})
                messagebox.showinfo(
                    "AI AIS Extraction Complete",
                    f"Extracted AIS data.\nTotal Income: Rs.{ai_data.get('total_income', 0):,}\nTotal TDS: Rs.{ai_data.get('total_tds', 0):,}\nConfidence: {ai_data.get('confidence', 0):.0%}"
                )
            elif result.get("status") == "disabled":
                messagebox.showwarning("AI Disabled", "AI is disabled. Enable it in Settings.")
            else:
                messagebox.showerror("AI Error", result.get("error", "Unknown error"))

        ImportService.extract_ais_with_ai(
            ais_json=ais_json,
            root_window=root_window,
            on_result=on_ai_result
        )

    except Exception as e:
        messagebox.showerror("Error", f"Failed to import AIS: {e}")


def _handle_tax_advisory(parent, form_vars):
    """Handle AI tax advisory request."""
    from tkinter import messagebox
    from src.services.io.import_service import ImportService

    root_window = parent.winfo_toplevel()

    # Build vardict from form_vars
    vardict = {
        "income": {
            "sal_gross": form_vars.get("sal_gross", 0) or 0,
            "os_dividend": [],
            "total_income": form_vars.get("total_income", 0) or 0
        },
        "deductions": {
            "ded_16ia": form_vars.get("ded_16ia", 0) or 0
        }
    }

    def on_ai_result(result):
        if result.get("status") == "success":
            ai_data = result.get("data", {})
            suggestions = ai_data.get("tax_savings_suggestions", [])
            regime = ai_data.get("regime_comparison", {})
            alerts = ai_data.get("compliance_alerts", [])

            msg = "Tax Advisory Results\n\n"
            msg += "Tax Savings Suggestions:\n"
            for s in suggestions[:5]:
                msg += f"  - {s.get('section')}: {s.get('description', '')} (Savings: Rs.{s.get('potential_savings', 0):,})\n"

            if regime:
                msg += f"\nRegime Comparison:\n"
                msg += f"  New Regime: Rs.{regime.get('new_regime_tax', 0):,}\n"
                msg += f"  Old Regime: Rs.{regime.get('old_regime_tax', 0):,}\n"
                msg += f"  Recommendation: {regime.get('recommendation', 'N/A')}\n"

            if alerts:
                msg += f"\nCompliance Alerts:\n"
                for a in alerts[:3]:
                    msg += f"  - {a}\n"

            msg += f"\nConfidence: {ai_data.get('confidence', 0):.0%}"
            messagebox.showinfo("Tax Advisory", msg)
        elif result.get("status") == "disabled":
            messagebox.showwarning("AI Disabled", "AI is disabled. Enable it in Settings.")
        else:
            messagebox.showerror("AI Error", result.get("error", "Unknown error"))

    ImportService.get_tax_advisory(
        vardict=vardict,
        root_window=root_window,
        on_result=on_ai_result
    )


def _apply_ai_suggestions(form_vars, ai_data):
    """Apply AI extracted data to form variables."""
    field_mappings = {
        "sal_gross": "sal_gross",
        "sal_perks": "sal_perks",
        "sal_hra": "sal_hra",
        "sal_conveyance": "sal_conveyance",
        "sal_others": "sal_others",
        "ded_16ia": "ded_16ia",
        "ded_16ib": "ded_16ib",
        "ded_16ic": "ded_16ic",
    }

    applied = []
    for ai_field, form_field in field_mappings.items():
        if ai_field in ai_data and ai_data[ai_field] is not None:
            value = ai_data[ai_field]
            if form_field in form_vars:
                form_vars[form_field].set(str(int(value)))
                applied.append(form_field)

    return applied
