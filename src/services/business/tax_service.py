from typing import Dict, Any, Optional
from src.core.engine import ITREngine
from src.config import (
    STD_DEDUCTION_NEW_REGIME,
    HP_LET_OUT_STD_DEDUCTION_RATE,
    PRESUMPTIVE_44AD_RATE,
    PRESUMPTIVE_44AD_DIGITAL_RATE,
    PRESUMPTIVE_44ADA_RATE,
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
class TaxService:
    @staticmethod
    def _get_sf(vars_data: Dict[str, Any], key: str) -> float:
        try:
            v = vars_data.get(key)
            if not v:
                return 0.0
            val = v.get() if hasattr(v, 'get') else v
            if not val:
                return 0.0
            return float(str(val).replace(",", "").strip())
        except (ValueError, TypeError, AttributeError):
            return 0.0
    @staticmethod
    def calculate_net_tax(vars_data: dict) -> float:
        return float(vars_data.get("tax_net", 0) or 0)
    @staticmethod
    def calculate_gross_total_income(vars_data: Dict[str, Any]) -> float:
        sf = lambda k: TaxService._get_sf(vars_data, k)
        net_salary = TaxService._calculate_net_salary(vars_data, sf)
        hp_total = TaxService._calculate_house_property(vars_data, sf)
        bp_income = TaxService._calculate_business_income(vars_data, sf)
        cg_data = TaxService._calculate_capital_gains(vars_data, sf)
        vda_total = TaxService._calculate_vda(vars_data, sf)
        net_os = TaxService._calculate_other_sources(vars_data, sf)
        gti = (net_salary + max(0.0, hp_total) + bp_income +
               cg_data['ltcg_112a'] + cg_data['stcg_sum'] +
               cg_data['ltcg_112'] + vda_total + net_os)
        return gti
    @staticmethod
    def calculate_total_taxable_income(vars_data: Dict[str, Any]) -> float:
        gti = TaxService.calculate_gross_total_income(vars_data)
        sf = lambda k: TaxService._get_sf(vars_data, k)
        ded_total = sf("ded_80ccd2") + sf("ded_80cch") + sf("ded_80jjaa")
        tti = ITREngine.round_to_nearest_10(max(0.0, gti - ded_total))
        return tti
    @staticmethod
    def calculate_salary_income(vars_data: Dict[str, Any]) -> Dict[str, float]:
        sf = lambda k: TaxService._get_sf(vars_data, k)
        sal_std = STD_DEDUCTION_NEW_REGIME
        gross_salary = sf("sal_gross") + sf("sal_perks") + sf("sal_profits")
        net_salary = max(0.0, gross_salary - sf("sal_allowance") - sal_std)
        return {
            "gross_salary": gross_salary,
            "standard_deduction": sal_std,
            "allowances": sf("sal_allowance"),
            "net_salary": net_salary,
            "perquisites": sf("sal_perks"),
            "profits_in_lieu": sf("sal_profits")
        }
    @staticmethod
    def _calculate_net_salary(vars_data: Dict[str, Any], sf) -> float:
        sal_std = STD_DEDUCTION_NEW_REGIME
        gross_salary = sf("sal_gross") + sf("sal_perks") + sf("sal_profits")
        return max(0.0, gross_salary - sf("sal_allowance") - sal_std)
    @staticmethod
    def _calculate_house_property(vars_data: Dict[str, Any], sf) -> float:
        hp_total = 0.0
        for i in range(MAX_ENTRIES_HP):
            property_type = vars_data.get(f"hp_{i}_type")
            property_type = property_type.get() if hasattr(property_type, 'get') else "let-out"
            property_type = property_type.lower() if property_type else "let-out"
            rent = sf(f"hp_{i}_rent")
            muni_tax = sf(f"hp_{i}_muni_tax")
            interest_loan = sf(f"hp_{i}_int_loan")
            if property_type == "self-occupied":
                interest_loan = 0.0
                property_net = 0.0
            else:
                unrealised = sf(f"hp_{i}_unrealised_rent")
                nav = max(0.0, rent - unrealised - muni_tax)
                property_net = (nav - (nav * HP_LET_OUT_STD_DEDUCTION_RATE)) - interest_loan
            hp_total += property_net
        return hp_total
    @staticmethod
    def _calculate_business_income(vars_data: Dict[str, Any], sf) -> float:
        ad_total = 0.0
        for i in range(MAX_ENTRIES_44AD):
            digital = sf(f"ad_{i}_digital")
            turnover = sf(f"ad_{i}_turnover")
            ad_total += (digital * PRESUMPTIVE_44AD_DIGITAL_RATE) + \
                ((turnover - digital) * PRESUMPTIVE_44AD_RATE)
        ada_total = sum(sf(f"ada_{i}_gross") * PRESUMPTIVE_44ADA_RATE for i in range(MAX_ENTRIES_44ADA))
        ae_total = sum(sf(f"ae_{i}_amount") for i in range(MAX_ENTRIES_AE))
        bp_income = (
            ad_total + ada_total + ae_total +
            sf("bp_total_manual") +
            sf("msme_43b_disallowance") +
            sf("msme_interest_disallowance")
        )
        return bp_income
    @staticmethod
    def _calculate_capital_gains(vars_data: Dict[str, Any], sf) -> Dict[str, float]:
        ltcg_112a_total = 0.0
        for i in range(MAX_ENTRIES_CG):
            sale = sf(f"ltcg112a_{i}_sale")
            cost = sf(f"ltcg112a_{i}_cost")
            fmv = sf(f"ltcg112a_{i}_fmv")
            acquisition_cost = max(cost, min(fmv, sale)) if fmv > 0 else cost
            gain = max(0.0, sale - acquisition_cost)
            ltcg_112a_total += gain
        stcg_sum = 0.0
        for i in range(MAX_ENTRIES_CG):
            row_gain = max(0.0, sf(f"stcg_{i}_sale") - sf(f"stcg_{i}_cost"))
            stcg_sum += row_gain
        ltcg_112 = max(0.0, sf("ltcg_112_input") - sf("ltcg_112_exemption"))
        return {
            "ltcg_112a": ltcg_112a_total,
            "stcg_sum": stcg_sum,
            "ltcg_112": ltcg_112
        }
    @staticmethod
    def _calculate_vda(vars_data: Dict[str, Any], sf) -> float:
        return sum(max(0.0, sf(f"vda_{i}_sale") - sf(f"vda_{i}_cost"))
                   for i in range(MAX_ENTRIES_TCS))
    @staticmethod
    def _calculate_other_sources(vars_data: Dict[str, Any], sf) -> float:
        os_income_components = [
            "os_interest", "os_interest_it", "os_interest_other",
            "os_interest_concessional",
            "os_dividend", "os_dividend_foreign", "os_pension",
            "os_winnings", "os_other", "os_gift", "buyback_price",
        ]
        os_total_raw = sum(sf(comp) for comp in os_income_components)
        fp_deduction = ITREngine.calculate_family_pension_deduction(sf("os_pension"))
        return os_total_raw - fp_deduction
    @staticmethod
    def calculate_tax_breakdown(vars_data: Dict[str, Any]) -> Dict[str, float]:
        sf = lambda k: TaxService._get_sf(vars_data, k)
        tti = TaxService.calculate_total_taxable_income(vars_data)
        cg_data = TaxService._calculate_capital_gains(vars_data, sf)
        vda_total = TaxService._calculate_vda(vars_data, sf)
        ltcg_112a_total = cg_data['ltcg_112a']
        stcg_sum = cg_data['stcg_sum']
        ltcg_112 = cg_data['ltcg_112']
        special_incomes_total = ltcg_112a_total + stcg_sum + ltcg_112 + vda_total + sf("os_winnings")
        normal_income = max(0.0, tti - special_incomes_total)
        slab_tax = ITREngine.calculate_slab_tax(normal_income)
        shortfall = max(0.0, SLAB_TAX_FREE_LIMIT - normal_income)
        ltcg_taxes = ITREngine.calculate_ltcg_tax(ltcg_112a_total, ltcg_112, shortfall)
        stcg_tax = ITREngine.calculate_stcg_tax(stcg_sum, 0, max(0.0, shortfall - (ltcg_112 + ltcg_112a_total)))
        vda_tax = ITREngine.calculate_vda_tax(vda_total)
        winnings_tax = ITREngine.calculate_winnings_tax(sf("os_winnings"))
        tax_before_rebate = slab_tax + ltcg_taxes["total"] + stcg_tax + vda_tax + winnings_tax
        res_status = vars_data.get("filing_status")
        res_status = res_status.get() if hasattr(res_status, 'get') else ""
        is_resident = "non-resident" not in res_status.lower()
        rebate = ITREngine.calculate_87a_rebate(tti, slab_tax, is_resident)
        marginal_relief = ITREngine.calculate_marginal_relief_87a(tti, slab_tax, is_resident)
        total_rebate = rebate + marginal_relief
        tax_after_rebate = max(0.0, tax_before_rebate - total_rebate)
        div_income = sf("os_dividend") + sf("os_dividend_foreign")
        capped_income_total = stcg_sum + ltcg_112a_total + sf("ltcg_112_input") + div_income
        surcharge = ITREngine.calculate_surcharge(
            tti=tti,
            normal_tax=slab_tax - total_rebate,
            uncapped_special_tax=vda_tax + winnings_tax,
            capped_special_tax=ltcg_taxes["total"] + stcg_tax,
            non_capped_income=max(0.0, tti - capped_income_total),
            sp_inc_capped=capped_income_total
        )
        tax_after_surcharge = tax_after_rebate + surcharge
        cess = ITREngine.calculate_cess(tax_after_surcharge)
        return {
            "gross_total_income": TaxService.calculate_gross_total_income(vars_data),
            "total_deductions": sf("ded_80ccd2") + sf("ded_80cch") + sf("ded_80jjaa"),
            "total_taxable_income": tti,
            "normal_income": normal_income,
            "slab_tax": slab_tax,
            "ltcg_tax": ltcg_taxes["total"],
            "stcg_tax": stcg_tax,
            "vda_tax": vda_tax,
            "winnings_tax": winnings_tax,
            "tax_before_rebate": tax_before_rebate,
            "rebate_87a": total_rebate,
            "tax_after_rebate": tax_after_rebate,
            "surcharge": surcharge,
            "cess": cess,
            "total_tax_liability": tax_after_surcharge + cess
        }
    @staticmethod
    def get_tax_summary(vars_data: Dict[str, Any]) -> Dict[str, Any]:
        breakdown = TaxService.calculate_tax_breakdown(vars_data)
        sf = lambda k: TaxService._get_sf(vars_data, k)
        it_paid = sum(sf(f"tax_{i}_amount") for i in range(MAX_ENTRIES_TAX_PAID))
        tds_paid = sum(sf(f"tds_{i}_amount") for i in range(MAX_ENTRIES_TDS))
        tcs_paid = sum(sf(f"tcs_{i}_amount") for i in range(MAX_ENTRIES_TCS))
        total_paid = it_paid + tds_paid + tcs_paid
        return {
            "tax_liability": breakdown["total_tax_liability"],
            "tax_paid": total_paid,
            "refund_due": max(0.0, total_paid - breakdown["total_tax_liability"]),
            "tax_due": max(0.0, breakdown["total_tax_liability"] - total_paid),
            "breakdown": breakdown
        }