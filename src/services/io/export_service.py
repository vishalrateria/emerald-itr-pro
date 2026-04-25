from typing import Dict, Any
from datetime import datetime
from tkinter import filedialog, messagebox
from src.services.logging_service import log as logger
from src.services.io.persistence import safe_save_json
from src.services.io.itr_mapper_service import ITRMapperService


def validate_for_export(vars: Dict[str, Any], itr_type: str) -> list:
    errors = []

    pan = (
        vars.get("pan", "").get()
        if hasattr(vars.get("pan"), "get")
        else vars.get("pan", "")
    )
    if not pan or len(str(pan)) != 10:
        errors.append("Invalid PAN format.")

    bank_acc = (
        vars.get("bank_0_acc", "").get()
        if hasattr(vars.get("bank_0_acc"), "get")
        else ""
    )
    if not bank_acc:
        errors.append("Bank Account details are mandatory for Refunds.")

    if itr_type in ["ITR-4"]:
        ad_turnover = sum(
            float(vars.get(f"ad_{i}_turnover", "0").get() or 0)
            for i in range(10)
            if hasattr(vars.get(f"ad_{i}_turnover"), "get")
        )
        if ad_turnover > 0 and not bank_acc:
            errors.append(
                "Section 44AD declared: Bank Account Details are strictly mandatory."
            )

    tti = (
        float(vars.get("tti", "0").get() or 0) if hasattr(vars.get("tti"), "get") else 0
    )
    if tti > 5000000 and itr_type in ["ITR-2", "ITR-3", "ITR-4"]:
        al_total = sum(
            [
                (
                    float(vars.get("al_immovable", "0").get() or 0)
                    if hasattr(vars.get("al_immovable"), "get")
                    else 0
                ),
                (
                    float(vars.get("al_movable", "0").get() or 0)
                    if hasattr(vars.get("al_movable"), "get")
                    else 0
                ),
            ]
        )
        if al_total <= 0:
            errors.append(
                "Total Income > ₹50 Lakh. Schedule AL (Assets & Liabilities) is mandatory."
            )

    return errors


try:
    from fpdf import FPDF

    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False


class ExportService:
    @staticmethod
    def generate_pdf_draft(
        vars_dict: Dict[str, Any], summary_data: Dict[str, Any]
    ) -> None:
        if not FPDF_AVAILABLE:
            messagebox.showerror("Error", "fpdf2 not installed.")
            return

        from src.services.settings_service import SettingsManager

        default_dir = SettingsManager.get("Engine.pdf_save_path", "")

        kwargs = {"defaultextension": ".pdf", "filetypes": [("PDF", "*.pdf")]}
        if default_dir:
            kwargs["initialdir"] = default_dir

        path = filedialog.asksaveasfilename(**kwargs)
        if not path:
            return
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("helvetica", "B", 16)
            pdf.cell(0, 10, "EMERALD ITR PRO - DRAFT SUMMARY", ln=True, align="C")
            pdf.set_font("helvetica", "", 10)
            pdf.cell(
                0,
                10,
                f"PAN: {vars_dict['pan'].get().upper()} | AY: 2026-27",
                ln=True,
                align="C",
            )
            pdf.ln(10)
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(140, 8, "Description", border=1)
            pdf.cell(50, 8, "Amount (INR)", border=1, ln=True)
            pdf.set_font("helvetica", "", 10)
            for key, label in [
                ("gti", "Gross Total Income"),
                ("tti", "Total Taxable Income"),
                ("tax", "Tax Liability"),
            ]:
                pdf.cell(140, 8, label, border=1)
                pdf.cell(
                    50,
                    8,
                    f"{int(summary_data.get(key, 0)):,}",
                    border=1,
                    ln=True,
                    align="R",
                )
            pdf.output(path)
            messagebox.showinfo("Success", f"PDF saved to {path}")
        except Exception as e:
            logger.error(f"PDF Gen failed: {e}")
            messagebox.showerror("PDF Error", f"Failed to generate PDF draft:\n{e}")

    @staticmethod
    def export_itr_json(vars: Dict[str, Any], gti: float, itr_type: str) -> None:
        errors = validate_for_export(vars, itr_type)
        if errors:
            messagebox.showerror(
                "Validation Failed",
                "Cannot generate JSON due to statutory errors:\n" + "\n".join(errors),
            )
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("ITR JSON", "*.json")],
            initialfile=f"ITR_JSON_{datetime.now().strftime('%Y%m%d')}.json",
        )
        if not path:
            return
        try:
            data = ITRMapperService.map_to_itr(itr_type, vars)
            safe_save_json(path, data)
            messagebox.showinfo(
                "Export Success",
                f"{itr_type} JSON safely generated and mapped to {path}",
            )
        except Exception as e:
            logger.error(f"Export failed: {e}")
            messagebox.showerror("Export Error", str(e))
