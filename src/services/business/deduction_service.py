from typing import Dict, Any, List, Optional
from src.core.engine import ITREngine
from src.config import (
    STD_DEDUCTION_NEW_REGIME,
    FAMILY_PENSION_DEDUCTION_LIMIT,
    MAX_ENTRIES_HP,
    MAX_ENTRIES_44AD,
    MAX_ENTRIES_44ADA,
    PRESUMPTIVE_44AD_TURNOVER_LIMIT,
    PRESUMPTIVE_44AD_LIMIT_BASE,
    PRESUMPTIVE_44AD_LIMIT_ENHANCED,
    PRESUMPTIVE_44ADA_RECEIPTS_LIMIT_HIGH,
    PRESUMPTIVE_44ADA_RECEIPTS_LIMIT_LOW,
)


class DeductionService:
    @staticmethod
    def _get_sf(vars_data: Dict[str, Any], key: str) -> float:
        try:
            v = vars_data.get(key)
            if not v:
                return 0.0
            val = v.get() if hasattr(v, "get") else v
            if not val:
                return 0.0
            return float(str(val).replace(",", "").strip())
        except (ValueError, TypeError, AttributeError):
            return 0.0

    @staticmethod
    def calculate_total_deductions(vars_data: dict) -> float:
        return float(vars_data.get("ded_total", 0) or 0)

    @staticmethod
    def calculate_allowed_deductions(vars_data: Dict[str, Any]) -> Dict[str, float]:
        def sf(k):
            return DeductionService._get_sf(vars_data, k)

        deductions = {
            "ded_80ccd2": sf("ded_80ccd2"),
            "ded_80cch": sf("ded_80cch"),
            "ded_80jjaa": sf("ded_80jjaa"),
        }
        sal_gross = sf("sal_gross")
        if deductions["ded_80ccd2"] > (sal_gross * 0.14):
            deductions["ded_80ccd2_limited"] = sal_gross * 0.14
        if deductions["ded_80ccd2"] > 750000:
            deductions["ded_80ccd2_limited"] = min(
                deductions.get("ded_80ccd2_limited", deductions["ded_80ccd2"]), 750000
            )
        total_allowed = sum(
            v for v in deductions.values() if isinstance(v, (int, float))
        )
        deductions["total_allowed"] = total_allowed
        return deductions

    @staticmethod
    def calculate_disallowed_deductions(vars_data: Dict[str, Any]) -> Dict[str, float]:
        def sf(k):
            return DeductionService._get_sf(vars_data, k)

        disallowed = {
            "ded_80c": sf("ded_80c"),
            "ded_80d": sf("ded_80d"),
            "ded_80d_1": sf("ded_80d_1"),
            "ded_80d_2": sf("ded_80d_2"),
            "ded_80e": sf("ded_80e"),
            "ded_80ee": sf("ded_80ee"),
            "ded_80eea": sf("ded_80eea"),
            "ded_80gg": sf("ded_80gg"),
            "ded_80tta": sf("ded_80tta"),
            "ded_80ttb": sf("ded_80ttb"),
            "sal_hra": sf("sal_hra"),
            "sal_lta": sf("sal_lta"),
            "ded_80g_0_amt": sf("ded_80g_0_amt"),
            "ded_80g_1_amt": sf("ded_80g_1_amt"),
            "ded_80g_2_amt": sf("ded_80g_2_amt"),
            "ded_80g_3_amt": sf("ded_80g_3_amt"),
            "ded_80g_4_amt": sf("ded_80g_4_amt"),
            "ded_80ggc": sf("ded_80ggc"),
        }
        total_disallowed = sum(
            v for v in disallowed.values() if isinstance(v, (int, float))
        )
        disallowed["total_disallowed"] = total_disallowed
        return disallowed

    @staticmethod
    def validate_deduction_limits(vars_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        def sf(k):
            return DeductionService._get_sf(vars_data, k)

        issues = []
        ded_80ccd2 = sf("ded_80ccd2")
        sal_gross = sf("sal_gross")
        if ded_80ccd2 > (sal_gross * 0.14):
            issues.append(
                {
                    "id": "WARN_80CCD2_LIMIT",
                    "type": "warning",
                    "message": f"80CCD(2) limit: Employer contribution {ded_80ccd2:,.0f} exceeds 14% of salary {sal_gross * 0.14:,.0f}",
                    "ruleId": "R_80CCD2_MAX",
                    "legalReference": "Section 80CCD(2)",
                }
            )
        if ded_80ccd2 > 750000:
            issues.append(
                {
                    "id": "ERR_PF_NPS_CEILING",
                    "type": "error",
                    "message": f"PF/NPS ceiling: Employer contribution {ded_80ccd2:,.0f} exceeds statutory limit of Rs. 7,50,000",
                    "ruleId": "R_RET_CEILING",
                    "legalReference": "Section 17(2)(vii)",
                }
            )
        return issues

    @staticmethod
    def calculate_standard_deduction(vars_data: Dict[str, Any]) -> Dict[str, float]:
        def sf(k):
            return DeductionService._get_sf(vars_data, k)

        sal_gross = sf("sal_gross")
        os_pension = sf("os_pension")
        sal_std = STD_DEDUCTION_NEW_REGIME if sal_gross > 0 else 0
        fp_deduction = ITREngine.calculate_family_pension_deduction(os_pension)
        return {
            "sal_std_ded": sal_std,
            "os_family_pension_ded": fp_deduction,
            "total_std_deduction": sal_std + fp_deduction,
        }

    @staticmethod
    def calculate_presumptive_limits(vars_data: Dict[str, Any]) -> Dict[str, Any]:
        def sf(k):
            return DeductionService._get_sf(vars_data, k)

        turnover_44ad = sum(sf(f"ad_{i}_turnover") for i in range(MAX_ENTRIES_44AD))
        receipts_44ada = sum(sf(f"ada_{i}_gross") for i in range(MAX_ENTRIES_44ADA))
        cash_slab = vars_data.get("cash_txn_slab")
        cash_slab = cash_slab.get() if hasattr(cash_slab, "get") else "<= 5%"
        if cash_slab == "<= 5%":
            limit_44ad = PRESUMPTIVE_44AD_LIMIT_ENHANCED
            limit_44ada = PRESUMPTIVE_44ADA_RECEIPTS_LIMIT_HIGH
        else:
            limit_44ad = PRESUMPTIVE_44AD_LIMIT_BASE
            limit_44ada = PRESUMPTIVE_44ADA_RECEIPTS_LIMIT_LOW
        issues = []
        if turnover_44ad > limit_44ad:
            issues.append(
                {
                    "id": "ERR_44AD_LIMIT",
                    "type": "error",
                    "message": f"44AD turnover {turnover_44ad:,.0f} exceeds limit {limit_44ad:,.0f}",
                    "ruleId": "R_44AD_LIMIT",
                }
            )
        if receipts_44ada > limit_44ada:
            issues.append(
                {
                    "id": "ERR_44ADA_LIMIT",
                    "type": "error",
                    "message": f"44ADA receipts {receipts_44ada:,.0f} exceeds limit {limit_44ada:,.0f}",
                    "ruleId": "R_44ADA_LIMIT",
                }
            )
        return {
            "turnover_44ad": turnover_44ad,
            "limit_44ad": limit_44ad,
            "receipts_44ada": receipts_44ada,
            "limit_44ada": limit_44ada,
            "cash_slab": cash_slab,
            "issues": issues,
            "44ad_eligible": turnover_44ad <= limit_44ad,
            "44ada_eligible": receipts_44ada <= limit_44ada,
        }

    @staticmethod
    def get_deduction_summary(vars_data: Dict[str, Any]) -> Dict[str, Any]:
        allowed = DeductionService.calculate_allowed_deductions(vars_data)
        disallowed = DeductionService.calculate_disallowed_deductions(vars_data)
        std_ded = DeductionService.calculate_standard_deduction(vars_data)
        presumptive = DeductionService.calculate_presumptive_limits(vars_data)
        validation = DeductionService.validate_deduction_limits(vars_data)
        return {
            "allowed_deductions": allowed,
            "disallowed_deductions": disallowed,
            "standard_deductions": std_ded,
            "presumptive_limits": presumptive,
            "validation_issues": validation,
            "total_allowed": allowed.get("total_allowed", 0),
            "total_disallowed": disallowed.get("total_disallowed", 0),
            "total_std_deduction": std_ded["total_std_deduction"],
        }
