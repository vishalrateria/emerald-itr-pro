import re
from datetime import datetime
from decimal import Decimal
from src.services.logging_service import log as logger
from src.config import (
    NEW_REGIME_SLABS,
    SLAB_TAX_FREE_LIMIT,
    REBATE_87A_MAX,
    REBATE_87A_THRESHOLD,
    LTCG_112A_EXEMPTION_LIMIT,
    LTCG_112A_TAX_RATE,
    STCG_111A_TAX_RATE,
    LTCG_112_TAX_RATE,
    VDA_TAX_RATE,
    SURCHARGE_THRESHOLD_10,
    SURCHARGE_THRESHOLD_15,
    SURCHARGE_THRESHOLD_25,
    HEALTH_EDUCATION_CESS_RATE,
    FY_DUE_DATE_ITR1,
    FY_DUE_DATE_ITR4,
    FY_REVISED_FREE_LIMIT,
    FY_REVISED_END_DATE,
    FAMILY_PENSION_DEDUCTION_LIMIT,
    MAX_ENTRIES_HP,
    MAX_ENTRIES_TDS,
    MAX_ENTRIES_TCS,
    MAX_ENTRIES_G,
    MAX_ENTRIES_VDA,
    MAX_ENTRIES_AE,
    MAX_ENTRIES_BANK,
    MAX_ENTRIES_44AD,
    MAX_ENTRIES_44ADA,
    PRESUMPTIVE_44AD_LIMIT_BASE,
    PRESUMPTIVE_44AD_LIMIT_ENHANCED,
    PRESUMPTIVE_44ADA_RECEIPTS_LIMIT_LOW,
    PRESUMPTIVE_44ADA_RECEIPTS_LIMIT_HIGH,
    ITR1_GTI_LIMIT,
    ITR1_HP_PROPERTY_LIMIT,
)


def round_to_nearest_10(val: float) -> int:
    if val is None:
        return 0
    return int((val + 5) // 10) * 10


def _parse_date_safely(date_str: str, context: str = "date parsing"):
    try:
        return datetime.strptime(date_str, "%d-%m-%Y")
    except (ValueError, TypeError):
        logger.error(
            f"❌ DATE PARSE ERROR ({context}): Invalid date format '{date_str}'. Expected DD-MM-YYYY."
        )
        return None


def calculate_slab_tax(t: float) -> float:
    if t is None or t < 0:
        return 0.0
    tax, prev = 0.0, 0.0
    for ceiling, rate in NEW_REGIME_SLABS:
        if t <= prev:
            break
        tax += (min(t, ceiling) - prev) * rate
        prev = ceiling
    return tax


def calculate_slab_tax_with_agri(t: float, agri_income: float) -> float:
    if agri_income <= 5000:
        return calculate_slab_tax(t)
    tax_total = calculate_slab_tax(t + agri_income)
    tax_agri = calculate_slab_tax(SLAB_TAX_FREE_LIMIT + agri_income)
    return max(0.0, tax_total - tax_agri)


def calculate_87a_rebate(
    tti: float, slab_tax: float, is_resident: bool = True
) -> float:
    if tti is None or tti < 0 or not is_resident or tti > REBATE_87A_THRESHOLD:
        return 0.0
    valid_slab_tax = max(0.0, min(slab_tax, tti))
    return min(valid_slab_tax, REBATE_87A_MAX)


def calculate_marginal_relief_87a(
    tti: float, slab_tax: float, is_resident: bool = True
) -> float:
    if not is_resident or tti <= REBATE_87A_THRESHOLD:
        return 0.0
    excess_income = tti - REBATE_87A_THRESHOLD
    return max(0.0, slab_tax - excess_income)


def calculate_ltcg_tax(
    ltcg_112a: float, ltcg_112: float = 0.0, exemption_shortfall: float = 0.0
) -> dict:
    taxable_112 = max(0.0, (ltcg_112 or 0.0) - exemption_shortfall)
    remaining_shortfall = max(0.0, exemption_shortfall - (ltcg_112 or 0.0))
    taxable_112a = max(
        0.0,
        max(0.0, (ltcg_112a or 0.0) - LTCG_112A_EXEMPTION_LIMIT) - remaining_shortfall,
    )
    t112, t112a = taxable_112 * LTCG_112_TAX_RATE, taxable_112a * LTCG_112A_TAX_RATE
    return {"112": t112, "112A": t112a, "total": t112 + t112a}


def calculate_stcg_tax(
    stcg_111a: float, exemption_shortfall: float = 0.0
) -> float:
    return max(0.0, (stcg_111a or 0.0) - exemption_shortfall) * STCG_111A_TAX_RATE


def calculate_vda_tax(vda_gains: float) -> float:
    return max(0.0, vda_gains or 0.0) * VDA_TAX_RATE


def calculate_winnings_tax(winnings: float) -> float:
    return max(0.0, winnings or 0.0) * 0.30


def calculate_ltcg_transitional_relief(
    sale_price: float,
    cost_of_acquisition: float,
    acquisition_date: str,
    indexation_cost: float,
) -> dict:
    try:
        cutoff = datetime.strptime("2024-07-22", "%Y-%m-%d")
        acq_date = datetime.strptime(acquisition_date, "%Y-%m-%d")
        if acq_date <= cutoff:
            t_no = max(0, (sale_price - cost_of_acquisition) * 0.125)
            t_with = max(0, (sale_price - indexation_cost) * 0.20)
            return {
                "eligible": True,
                "tax_no_index": t_no,
                "tax_with_index": t_with,
                "recommended": min(t_no, t_with),
                "method": "no_index" if t_no < t_with else "with_index",
            }
    except (ValueError, TypeError):
        pass
    return {
        "eligible": False,
        "tax_no_index": 0,
        "tax_with_index": 0,
        "recommended": 0,
        "method": None,
    }


def calculate_surcharge(
    tti: float,
    normal_tax: float,
    capped_special_tax: float = 0.0,
    uncapped_special_tax: float = 0.0,
    non_capped_income: float = None,
    sp_inc_capped: float = 0.0,
    agri_income: float = 0.0,
) -> float:
    if tti is None or tti <= SURCHARGE_THRESHOLD_10:
        return 0.0
    base_tax = normal_tax + uncapped_special_tax
    nci = tti if non_capped_income is None else non_capped_income

    def _rates(ti, bi):
        if ti <= SURCHARGE_THRESHOLD_10:
            return 0.0, 0.0
        if ti <= SURCHARGE_THRESHOLD_15:
            return 0.10, 0.10
        if ti <= SURCHARGE_THRESHOLD_25:
            return 0.15, 0.15
        return (0.25, 0.15) if bi > SURCHARGE_THRESHOLD_25 else (0.15, 0.15)

    br, cr = _rates(tti, nci)
    calc_sur = (base_tax * br) + (capped_special_tax * cr)
    for threshold in [
        SURCHARGE_THRESHOLD_25,
        SURCHARGE_THRESHOLD_15,
        SURCHARGE_THRESHOLD_10,
    ]:
        if tti > threshold:
            excess = tti - threshold
            tot_sp = capped_special_tax + uncapped_special_tax
            norm_real = max(0.0, tti - sp_inc_capped)
            ratio, t_bound = 0.0, 0.0
            if norm_real >= excess:
                t_bound = (
                    calculate_slab_tax_with_agri(norm_real - excess, agri_income)
                    + tot_sp
                )
            elif sp_inc_capped > 0:
                ratio = max(0.0, (sp_inc_capped - (excess - norm_real)) / sp_inc_capped)
                t_bound = (capped_special_tax * ratio) + uncapped_special_tax
            br_th, cr_th = _rates(threshold, max(0.0, nci - excess))
            app_cap = capped_special_tax * ratio if sp_inc_capped > 0 else 0.0
            sur_bound = (t_bound - app_cap) * br_th + (app_cap * cr_th)
            max_liab = t_bound + sur_bound + excess
            if (base_tax + capped_special_tax + calc_sur) > max_liab:
                calc_sur = min(
                    calc_sur, max(0.0, max_liab - (base_tax + capped_special_tax))
                )
    return calc_sur


def calculate_cess(tax_after_surcharge: float) -> float:
    return max(0.0, (tax_after_surcharge or 0.0) * HEALTH_EDUCATION_CESS_RATE)


def calculate_234a_interest(
    tax_due: float, filing_date_str: str, itr_type: str = "ITR-1"
) -> float:
    if tax_due <= 0 or not filing_date_str:
        return 0.0
    f_date = _parse_date_safely(filing_date_str, "234A")
    if not f_date:
        return 0.0
    due = FY_DUE_DATE_ITR4 if itr_type in ["ITR-3", "ITR-4"] else FY_DUE_DATE_ITR1
    if f_date <= due:
        return 0.0
    diff = (f_date.year - due.year) * 12 + (f_date.month - due.month)
    if f_date.day > due.day:
        diff += 1
    return float(
        (Decimal(str(tax_due)) * Decimal("0.01") * Decimal(str(max(0, diff)))).quantize(
            Decimal("1")
        )
    )


def calculate_234b_interest(
    assessed_tax: float,
    installments: list,
    months_delayed: int = 0,
    is_senior_citizen: bool = False,
    has_business_income: bool = False,
) -> float:
    if is_senior_citizen and not has_business_income:
        return 0.0
    if assessed_tax < 10000 or sum(installments) >= (assessed_tax * 0.9):
        return 0.0
    shortfall = max(0.0, assessed_tax - sum(installments))
    m = max(1, months_delayed)
    return float(
        (Decimal(str(shortfall)) * Decimal("0.01") * Decimal(str(m))).quantize(
            Decimal("1")
        )
    )


def calculate_234c_interest(
    total_tax: float,
    installments: list,
    cg_winnings_tax_per_q: list = None,
    is_senior_citizen: bool = False,
    has_business_income: bool = False,
) -> float:
    if is_senior_citizen and not has_business_income:
        return 0.0
    if total_tax < 10000:
        return 0.0
    targets, relaxation, periods = (
        [0.15, 0.45, 0.75, 1.00],
        [0.12, 0.36, 0.75, 1.00],
        [3, 3, 3, 1],
    )
    interest, cg = 0.0, cg_winnings_tax_per_q or [0, 0, 0, 0]
    cum_paid, running = [0.0] * 4, 0.0
    for i in range(4):
        running += installments[i]
        cum_paid[i] = running
    for i in range(4):
        stake = total_tax - sum(cg[i + 1 :])
        if cum_paid[i] < (stake * relaxation[i]):
            interest += max(0.0, (stake * targets[i]) - cum_paid[i]) * 0.01 * periods[i]
    return float(int(interest))


def calculate_234f_fee(
    tti: float, filing_date_str: str, itr_type: str = "ITR-1"
) -> float:
    if not filing_date_str:
        return 0.0
    f_date = _parse_date_safely(filing_date_str, "234F")
    due = FY_DUE_DATE_ITR4 if itr_type in ["ITR-3", "ITR-4"] else FY_DUE_DATE_ITR1
    if not f_date or f_date <= due or tti <= SLAB_TAX_FREE_LIMIT:
        return 0.0
    return 1000.0 if tti <= 500000 else 5000.0


def calculate_234i_fee(
    tti: float, filing_date_str: str, is_revised: bool = False
) -> float:
    if not is_revised or not filing_date_str:
        return 0.0
    f_date = _parse_date_safely(filing_date_str, "234I")
    if f_date and FY_REVISED_FREE_LIMIT < f_date <= FY_REVISED_END_DATE:
        return 1000.0 if tti <= 500000 else 5000.0
    return 0.0


def calculate_family_pension_deduction(amount: float) -> float:
    return min(amount / 3.0, FAMILY_PENSION_DEDUCTION_LIMIT) if amount > 0 else 0.0


def validate_deduction_limits(vars_data: dict, gti: float) -> list:
    def _f(fid, msg, level="info", rid=None, ref=None):
        return {
            "id": fid,
            "message": msg,
            "type": level,
            "ruleId": rid or fid,
            "legalReference": ref,
        }

    w, sf = [], lambda k: float(vars_data.get(k, 0) or 0)
    if sf("ded_80ccd2") > (sf("sal_gross") * 0.14):
        w.append(
            _f(
                "WARN_80CCD2_LIMIT",
                "⚠️ 80CCD(2) LIMIT: Employer contribution exceeds 14% of Salary",
                "warning",
                "R_80CCD2_MAX",
                "Section 80CCD(2)",
            )
        )
    if sf("ded_80ccd2") > 750000:
        w.append(
            _f(
                "ERR_PF_NPS_CEILING",
                "❌ PF/NPS CEILING: Employer contribution exceeds ₹7.5L statutory limit",
                "error",
                "R_RET_CEILING",
                "Section 17(2)(vii)",
            )
        )
    for k, msg in [
        ("ded_80ccd1b", "80CCD(1B)"),
        ("ded_80c", "80C"),
        ("ded_80d", "80D"),
        ("sal_hra", "HRA"),
    ]:
        if sf(k) > 0:
            w.append(
                _f(
                    f"ERR_{k.upper()}_DISALLOWED",
                    f"❌ {msg}: Not allowed in New Regime",
                    "error",
                    "R_115BAC_DED",
                    "Section 115BAC",
                )
            )
    if sf("hp_total") < 0:
        w.append(
            _f(
                "ERR_HP_LOSS_SETOFF",
                "❌ HP LOSS: No set-off in New Regime",
                "error",
                "R_115BAC_LOSS",
            )
        )
    if sf("os_pension") > 0:
        correct = calculate_family_pension_deduction(sf("os_pension"))
        if abs(sf("os_family_pension_ded") - correct) > 1:
            w.append(
                _f(
                    "INFO_FP_DEDUCTION",
                    f"ℹ️ FAMILY PENSION: Deduction should be ₹{int(correct):,}",
                    "info",
                    "R_FP_DED",
                )
            )
    return w


def is_specified_debt_fund(purchase_date_str: str, debt_exposure: float) -> bool:
    if not purchase_date_str or debt_exposure < 65:
        return False
    p_date = _parse_date_safely(purchase_date_str, "Debt MF")
    return p_date >= datetime(2023, 4, 1) if p_date else False


def bucket_advance_tax(tax_entries: list) -> list:
    buckets = [0.0] * 4
    milestones = [
        datetime(2025, 6, 15),
        datetime(2025, 9, 15),
        datetime(2025, 12, 15),
        datetime(2026, 3, 15),
    ]
    for entry in tax_entries:
        if "advance" in str(entry.get("type", "")).lower():
            d = _parse_date_safely(entry.get("date", ""), "Advance Tax")
            if d:
                for i, m in enumerate(milestones):
                    if d <= m:
                        buckets[i] += float(entry.get("amount", 0) or 0)
    return buckets


def calculate_net_winnings_rule133(
    total_winnings: float, deposits: float, opening_bal: float
) -> float:
    return max(0.0, total_winnings - (deposits + opening_bal))


def perform_audit_scan(
    vars_data: dict, gti: float, tti: float, due_tax: float, itr_type: str = "ITR-4"
) -> list:
    def _f(fid, msg, level="info"):
        return {"id": fid, "message": msg, "type": level}

    if gti is None or tti is None or due_tax is None:
        return [_f("ERR_MISSING", "❌ Missing required calculation values.", "error")]
    faults = []

    def sf(k, default=0):
        return float(vars_data.get(k, default) or 0)

    if itr_type == "ITR-4":
        turnover = sum(sf(f"ad_{i}_turnover") for i in range(MAX_ENTRIES_44AD))
        if turnover > 0:
            limit = (
                PRESUMPTIVE_44AD_LIMIT_ENHANCED
                if vars_data.get("cash_txn_slab") == "<= 5%"
                else PRESUMPTIVE_44AD_LIMIT_BASE
            )
            if turnover > limit:
                faults.append(
                    _f("ERR_44AD_LIMIT", "❌ Turnover exceeds 44AD limit.", "error")
                )
    pan = vars_data.get("pan", "").upper()
    if pan and not re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", pan):
        faults.append(_f("ERR_PAN", "❌ Invalid PAN format.", "error"))
    if tti > 5000000 and (sf("al_immovable") + sf("al_movable")) == 0:
        faults.append(_f("ERR_AL", "❌ Schedule AL mandatory > ₹50L.", "error"))
    faults.extend(validate_deduction_limits(vars_data, gti))
    return faults if faults else [_f("OK", "✅ STATUS: COMPLIANT", "info")]


class ITREngine:
    calculate_slab_tax = staticmethod(calculate_slab_tax)
    calculate_slab_tax_with_agri = staticmethod(calculate_slab_tax_with_agri)
    calculate_87a_rebate = staticmethod(calculate_87a_rebate)
    calculate_marginal_relief_87a = staticmethod(calculate_marginal_relief_87a)
    calculate_ltcg_tax = staticmethod(calculate_ltcg_tax)
    calculate_stcg_tax = staticmethod(calculate_stcg_tax)
    calculate_vda_tax = staticmethod(calculate_vda_tax)
    calculate_winnings_tax = staticmethod(calculate_winnings_tax)
    calculate_ltcg_transitional_relief = staticmethod(
        calculate_ltcg_transitional_relief
    )
    calculate_surcharge = staticmethod(calculate_surcharge)
    calculate_cess = staticmethod(calculate_cess)
    calculate_234a_interest = staticmethod(calculate_234a_interest)
    calculate_234b_interest = staticmethod(calculate_234b_interest)
    calculate_234c_interest = staticmethod(calculate_234c_interest)
    calculate_234f_fee = staticmethod(calculate_234f_fee)
    calculate_234i_fee = staticmethod(calculate_234i_fee)
    calculate_family_pension_deduction = staticmethod(
        calculate_family_pension_deduction
    )
    validate_deduction_limits = staticmethod(validate_deduction_limits)
    perform_audit_scan = staticmethod(perform_audit_scan)
    round_to_nearest_10 = staticmethod(round_to_nearest_10)
    _parse_date_safely = staticmethod(_parse_date_safely)
    bucket_advance_tax = staticmethod(bucket_advance_tax)
    is_specified_debt_fund = staticmethod(is_specified_debt_fund)
    calculate_net_winnings_rule133 = staticmethod(calculate_net_winnings_rule133)
