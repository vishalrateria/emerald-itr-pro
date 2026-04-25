from typing import Dict, Any, Optional
import os
import csv
import re
import json
from datetime import datetime
from tkinter import filedialog, messagebox
from src.services.logging_service import log as logger

try:
    import openpyxl

    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

try:
    import pypdf

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


class ImportService:
    ais_cache = {}

    @staticmethod
    def _validate_path(path: str) -> bool:
        try:
            resolved = os.path.abspath(path)
            return os.path.isfile(resolved)
        except Exception:
            return False

    @staticmethod
    def import_trial_balance(form_vars: Dict[str, Any]) -> None:
        path = filedialog.askopenfilename(filetypes=[("Data Files", "*.csv;*.xlsx")])
        if not path or not ImportService._validate_path(path):
            return
        mapping = {
            "sales": "tb_sales",
            "purchase": "tb_purchase",
            "direct income": "tb_dir_income",
            "direct expense": "tb_dir_exp",
            "indirect income": "tb_ind_income",
            "indirect expense": "tb_ind_exp",
            "salaries": "tb_sal",
            "rent": "tb_rent",
        }
        imported = 0
        try:
            if path.endswith(".csv"):
                with open(path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        acc = str(row.get("Account", "")).lower()
                        amt = row.get("Amount", row.get("Debit", "0")).replace(",", "")
                        for pattern, key in mapping.items():
                            if pattern in acc and key in form_vars:
                                form_vars[key].set(str(int(float(amt))))
                                imported += 1
            elif path.endswith(".xlsx") and EXCEL_AVAILABLE:
                wb = openpyxl.load_workbook(path, data_only=True)
                ws = wb.active
                for row in ws.iter_rows(min_row=2, values_only=True):
                    acc = str(row[0]).lower() if row[0] else ""
                    amt = str(row[1]).replace(",", "") if row[1] else "0"
                    for pattern, key in mapping.items():
                        if pattern in acc and key in form_vars:
                            form_vars[key].set(str(int(float(amt))))
                            imported += 1
            messagebox.showinfo("Import Success", f"Updated {imported} fields.")
        except Exception as e:
            logger.error(f"Import failed: {e}")
            messagebox.showerror("Error", f"Import failed: {e}")

    @staticmethod
    def import_prefill(form_vars: Dict[str, Any]) -> None:
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not path or not ImportService._validate_path(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            itr_key = next(
                (
                    k
                    for k in ["ITR1", "ITR2", "ITR3", "ITR4"]
                    if k in data.get("ITR", {})
                ),
                None,
            )
            if not itr_key:
                raise ValueError("Official ITD ITR Schema not found in JSON.")

            itr = data["ITR"][itr_key]

            p = itr.get("PartA_GEN1", {}).get("PersonalInfo", {}) or itr.get(
                "PersonalInfo", {}
            )
            if "PAN" in p:
                form_vars["pan"].set(p["PAN"])
            if "AssesseeName" in p and "FirstName" in p["AssesseeName"]:
                form_vars["name"].set(p["AssesseeName"]["FirstName"])
            if "DOB" in p:
                form_vars["dob"].set(p["DOB"])

            sal = itr.get("PartB_TI", {}).get("Salaries", {}) or itr.get(
                "IncomeDetails", {}
            ).get("Salary", {})
            if "GrossSalary" in sal:
                form_vars["sal_gross"].set(str(sal["GrossSalary"]))
            if "StandardDeduction" in sal:
                form_vars["sal_std_ded"].set(str(sal["StandardDeduction"]))

            chap6 = itr.get("PartB_TI", {}).get("ChapterVIA", {})
            if "Section80CCD2" in chap6:
                form_vars["ded_80ccd2"].set(str(chap6["Section80CCD2"]))
            if "Section80JJAA" in chap6:
                form_vars["ded_80jjaa"].set(str(chap6["Section80JJAA"]))

            messagebox.showinfo(
                "Success",
                f"Prefill data from {itr_key} officially imported and mapped.",
            )
        except Exception as e:
            logger.error(f"Prefill import failed: {e}")
            messagebox.showerror(
                "Import Error", f"Failed to import pre-fill JSON:\n{e}"
            )

    @staticmethod
    def import_form16_pdf(form_vars: Dict[str, Any]) -> None:
        if not PYPDF_AVAILABLE:
            messagebox.showerror("Error", "pypdf not installed.")
            return
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not path:
            return
        try:
            with open(path, "rb") as f:
                reader = pypdf.PdfReader(f)
                text = "\n".join(p.extract_text() for p in reader.pages)

                tan = re.search(r"[A-Z]{4}[0-9]{5}[A-Z]", text)
                if tan:
                    form_vars["tds_0_tan"].set(tan.group(0))

                gross_sal = re.search(r"Gross Salary.*?(\d{3,})", text, re.IGNORECASE)
                if gross_sal:
                    form_vars["sal_gross"].set(gross_sal.group(1))

                messagebox.showinfo(
                    "Success", "Form 16 Data (TAN, Salary) seamlessly extracted."
                )
        except Exception as e:
            logger.error(f"PDF Import failed: {e}")
            messagebox.showerror("PDF Error", f"Failed to parse PDF:\n{e}")

    @staticmethod
    def import_ais_json(form_vars: Dict[str, Any]) -> None:
        path = filedialog.askopenfilename(filetypes=[("AIS JSON", "*.json")])
        if not path or not ImportService._validate_path(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            ImportService.ais_cache = data

            total_div = sum(
                float(item.get("amount", 0))
                for item in data.get("dividend_entries", [])
            )
            total_int = sum(
                float(item.get("amount", 0))
                for item in data.get("interest_entries", [])
            )

            if total_div > 0 and "os_dividend" in form_vars:
                form_vars["os_dividend"].set(str(int(total_div)))
            if total_int > 0 and "os_interest" in form_vars:
                form_vars["os_interest"].set(str(int(total_int)))

            messagebox.showinfo(
                "Success",
                "AIS data loaded and automatically reconciled to OS schedules.",
            )
        except Exception as e:
            logger.error(f"AIS import failed: {e}")
            messagebox.showerror("AIS Error", f"Failed to load AIS JSON:\n{e}")

    @staticmethod
    def extract_with_ai(text: str, root_window=None, on_result: callable = None):
        try:
            from src.services.ai.ai_manager import get_ai_manager

            ai_manager = get_ai_manager()

            if not ai_manager.is_enabled():
                logger.info("AI is disabled in settings")
                return None

            def handle_result(result):
                if root_window and on_result:
                    root_window.after(0, lambda r=result: on_result(r))
                elif on_result:
                    on_result(result)

            ai_manager.extract_data_async(
                text=text, schema_type="form16", callback=handle_result
            )

            logger.info("AI extraction started asynchronously")
            return True

        except ImportError as e:
            logger.warning(f"AI services not available: {e}")
            return None
        except Exception as e:
            logger.error(f"AI extraction failed: {e}")
            return None

    @staticmethod
    def run_ai_audit(vardict: dict, root_window=None, on_result: callable = None):
        try:
            from src.services.ai.ai_manager import get_ai_manager

            ai_manager = get_ai_manager()

            if not ai_manager.is_enabled():
                logger.info("AI is disabled in settings")
                return None

            def handle_result(result):
                if root_window and on_result:
                    root_window.after(0, lambda r=result: on_result(r))
                elif on_result:
                    on_result(result)

            ai_manager.audit_vardict_async(vardict=vardict, callback=handle_result)

            logger.info("AI audit started asynchronously")
            return True

        except ImportError as e:
            logger.warning(f"AI services not available: {e}")
            return None
        except Exception as e:
            logger.error(f"AI audit failed: {e}")
            return None

    @staticmethod
    def extract_form26as_with_ai(
        text: str, root_window=None, on_result: callable = None
    ):
        try:
            from src.services.ai.ai_manager import get_ai_manager

            ai_manager = get_ai_manager()

            if not ai_manager.is_enabled():
                logger.info("AI is disabled in settings")
                return None

            def handle_result(result):
                if root_window and on_result:
                    root_window.after(0, lambda r=result: on_result(r))
                elif on_result:
                    on_result(result)

            ai_manager.extract_form26as_async(text=text, callback=handle_result)

            logger.info("AI Form 26AS extraction started")
            return True

        except ImportError as e:
            logger.warning(f"AI services not available: {e}")
            return None
        except Exception as e:
            logger.error(f"AI Form 26AS extraction failed: {e}")
            return None

    @staticmethod
    def extract_ais_with_ai(
        ais_json: str, root_window=None, on_result: callable = None
    ):
        try:
            from src.services.ai.ai_manager import get_ai_manager

            ai_manager = get_ai_manager()

            if not ai_manager.is_enabled():
                logger.info("AI is disabled in settings")
                return None

            def handle_result(result):
                if root_window and on_result:
                    root_window.after(0, lambda r=result: on_result(r))
                elif on_result:
                    on_result(result)

            ai_manager.extract_ais_async(ais_json=ais_json, callback=handle_result)

            logger.info("AI AIS extraction started")
            return True

        except ImportError as e:
            logger.warning(f"AI services not available: {e}")
            return None
        except Exception as e:
            logger.error(f"AI AIS extraction failed: {e}")
            return None

    @staticmethod
    def get_tax_advisory(vardict: dict, root_window=None, on_result: callable = None):
        try:
            from src.services.ai.ai_manager import get_ai_manager

            ai_manager = get_ai_manager()

            if not ai_manager.is_enabled():
                logger.info("AI is disabled in settings")
                return None

            def handle_result(result):
                if root_window and on_result:
                    root_window.after(0, lambda r=result: on_result(r))
                elif on_result:
                    on_result(result)

            ai_manager.get_tax_advisory_async(vardict=vardict, callback=handle_result)

            logger.info("AI tax advisory started")
            return True

        except ImportError as e:
            logger.warning(f"AI services not available: {e}")
            return None
        except Exception as e:
            logger.error(f"AI tax advisory failed: {e}")
            return None

    @staticmethod
    def classify_document(content: str, root_window=None, on_result: callable = None):
        try:
            from src.services.ai.ai_manager import get_ai_manager

            ai_manager = get_ai_manager()

            if not ai_manager.is_enabled():
                logger.info("AI is disabled in settings")
                return None

            def handle_result(result):
                if root_window and on_result:
                    root_window.after(0, lambda r=result: on_result(r))
                elif on_result:
                    on_result(result)

            ai_manager.classify_document_async(content=content, callback=handle_result)

            logger.info("AI document classification started")
            return True

        except ImportError as e:
            logger.warning(f"AI services not available: {e}")
            return None
        except Exception as e:
            logger.error(f"AI document classification failed: {e}")
            return None
