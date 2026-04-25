from typing import Any, Dict, List, Optional
from src.core.engine import ITREngine
from src.services.business.tax_service import TaxService
from src.services.business.deduction_service import DeductionService
from src.config import (
    SLAB_TAX_FREE_LIMIT,
    MAX_ENTRIES_TDS,
    MAX_ENTRIES_TCS,
    MAX_ENTRIES_AE,
    MAX_ENTRIES_HP,
    MAX_ENTRIES_VDA,
    MAX_ENTRIES_44AD,
    MAX_ENTRIES_44ADA,
    MAX_ENTRIES_CG,
    MAX_ENTRIES_TAX_PAID,
)


class TaxController:
    def __init__(self, app_instance: Any):
        self.app = app_instance

    def _get_sf(self, key: str) -> float:
        try:
            v = self.app.vars.get(key)
            if not v:
                return 0.0
            val = v.get()
            if not val:
                return 0.0
            return float(str(val).replace(",", "").strip())
        except (ValueError, TypeError, AttributeError):
            return 0.0

    def _vars_to_dict(self) -> Dict[str, Any]:
        result = {}
        for key, var in self.app.vars.items():
            try:
                result[key] = var.get() if hasattr(var, "get") else var
            except Exception:
                result[key] = ""
        return result

    def compute(self) -> bool:
        if getattr(self, "_is_computing", False):
            return True
        self._is_computing = True
        try:
            form_vars = self.app.vars
            sf = self._get_sf
            vars_dict = self._vars_to_dict()
            excluded_deductions = [
                "ded_80c",
                "ded_80d",
                "ded_80e",
                "ded_80tta",
                "ded_80ttb",
                "sal_hra",
                "sal_lta",
                "ded_80ggc",
                "ded_80g_0_amt",
                "ded_80g_1_amt",
                "ded_80g_2_amt",
                "ded_80g_3_amt",
                "ded_80g_4_amt",
            ]
            for key in excluded_deductions:
                if sf(key) != 0:
                    form_vars[key].set("0")
            gti = TaxService.calculate_gross_total_income(vars_dict)
            form_vars["gti"].set(str(int(gti)))
            ded_total = sf("ded_80ccd2") + sf("ded_80cch") + sf("ded_80jjaa")
            form_vars["ded_total"].set(str(int(ded_total)))
            tti = TaxService.calculate_total_taxable_income(vars_dict)
            form_vars["tti"].set(str(int(tti)))
            tax_results = self._handle_tax_calculation(form_vars, sf, tti, vars_dict)
            self._handle_interest_and_fees(form_vars, sf, tti, tax_results)
            return True
        finally:
            self._is_computing = False

    def _handle_tax_calculation(
        self, form_vars: Dict[str, Any], sf: Any, tti: float, vars_dict: Dict[str, Any]
    ) -> Dict[str, float]:
        breakdown = TaxService.calculate_tax_breakdown(vars_dict)
        form_vars["sal"].set(str(int(breakdown.get("normal_income", 0))))
        form_vars["sal_std_ded"].set(str(int(breakdown.get("total_std_deduction", 0))))
        form_vars["hp_total"].set(
            str(
                int(
                    breakdown.get("gross_total_income", 0)
                    - breakdown.get("normal_income", 0)
                )
            )
        )
        form_vars["bp_total"].set("0")
        form_vars["ltcg_112a_sum"].set("0")
        form_vars["stcg_sum"].set("0")
        form_vars["vda_sum"].set("0")
        form_vars["os_total"].set("0")
        form_vars["slab_tax"].set(str(int(breakdown.get("slab_tax", 0))))
        form_vars["ltcg_tax"].set(str(int(breakdown.get("ltcg_tax", 0))))
        form_vars["stcg_tax"].set(str(int(breakdown.get("stcg_tax", 0))))
        form_vars["vda_tax"].set(str(int(breakdown.get("vda_tax", 0))))
        form_vars["winnings_tax"].set(str(int(breakdown.get("winnings_tax", 0))))
        form_vars["rebate_87a"].set(str(int(breakdown.get("rebate_87a", 0))))
        form_vars["surcharge"].set(str(int(breakdown.get("surcharge", 0))))
        form_vars["cess"].set(str(int(breakdown.get("cess", 0))))
        return {
            "tax_after_surcharge": breakdown.get("tax_after_rebate", 0),
            "cess": breakdown.get("cess", 0),
        }

    def _handle_interest_and_fees(
        self,
        form_vars: Dict[str, Any],
        sf: Any,
        tti: float,
        tax_results: Dict[str, float],
    ) -> None:
        tax_after_surcharge = tax_results["tax_after_surcharge"]
        cess = tax_results["cess"]
        relief_89a = sf("relief_89a")
        tax_after_relief = max(0.0, tax_after_surcharge + cess - relief_89a)
        fee_234f = ITREngine.calculate_234f_fee(
            tti, form_vars["return_filing_date"].get(), self.app.selected_itr_type
        )
        form_vars["late_fee_234f"].set(str(int(fee_234f)))
        is_revised = (
            form_vars["is_revised_after_dec31"].get() or ""
        ).strip().lower() in ("yes", "1", "true")
        fee_234i = ITREngine.calculate_234i_fee(
            tti, form_vars["return_filing_date"].get(), is_revised
        )
        form_vars["fee_234i"].set(str(int(fee_234i)))
        advance_tax_entries = []
        for i in range(MAX_ENTRIES_TAX_PAID):
            t_var = form_vars.get(f"tax_{i}_type")
            t_type = t_var.get() if t_var else "Other"
            if "advance" in (t_type or "").lower():
                d_var = form_vars.get(f"tax_{i}_date")
                advance_tax_entries.append(
                    {
                        "date": d_var.get() if d_var else "",
                        "amount": sf(f"tax_{i}_amount"),
                        "type": "advance",
                    }
                )
        it_paid = sum(sf(f"tax_{i}_amount") for i in range(MAX_ENTRIES_TAX_PAID))
        tds_paid = sum(sf(f"tds_{i}_amount") for i in range(MAX_ENTRIES_TDS))
        tcs_paid = sum(sf(f"tcs_{i}_amount") for i in range(MAX_ENTRIES_TCS))
        credits_for_interest = (
            sum(e["amount"] for e in advance_tax_entries) + tds_paid + tcs_paid
        )
        tax_base_for_interest = tax_after_relief
        try:
            advance_buckets = ITREngine.bucket_advance_tax(advance_tax_entries)
            interest_234b = ITREngine.calculate_234b_interest(
                tax_base_for_interest, advance_buckets, int(sf("months_234b") or 0)
            )
            interest_234c = ITREngine.calculate_234c_interest(
                tax_base_for_interest, advance_buckets
            )
            interest_234a = ITREngine.calculate_234a_interest(
                max(0.0, tax_base_for_interest - credits_for_interest),
                form_vars["return_filing_date"].get(),
                self.app.selected_itr_type,
            )
            interest_total = interest_234a + interest_234b + interest_234c
        except Exception:
            interest_total = 0.0
        form_vars["interest_total"].set(str(int(interest_total)))
        total_tax_liability = (
            tax_base_for_interest + interest_total + fee_234f + fee_234i
        )
        form_vars["tax_total"].set(
            str(ITREngine.round_to_nearest_10(total_tax_liability))
        )
        it_total = it_paid + tds_paid + tcs_paid
        form_vars["it_total"].set(str(int(it_total)))
        tax_net = total_tax_liability - it_total
        form_vars["tax_net"].set(str(ITREngine.round_to_nearest_10(tax_net)))
        form_vars["due_tax"].set(str(ITREngine.round_to_nearest_10(max(0, tax_net))))

    def get_tax_summary(self) -> Dict[str, Any]:
        return TaxService.get_tax_summary(self._vars_to_dict())

    def get_deduction_summary(self) -> Dict[str, Any]:
        return DeductionService.get_deduction_summary(self._vars_to_dict())

    def validate_deductions(self) -> List[Dict[str, Any]]:
        return DeductionService.validate_deduction_limits(self._vars_to_dict())
