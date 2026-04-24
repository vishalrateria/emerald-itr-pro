import customtkinter as ctk
from src.config import (
    STD_DEDUCTION_NEW_REGIME, MAX_ENTRIES_44AD, MAX_ENTRIES_44ADA,
    MAX_BUSINESS_ENTITIES, MAX_ENTRIES_BANK, MAX_ENTRIES_TDS,
    MAX_ENTRIES_TCS, MAX_ENTRIES_TAX_PAID, MAX_ENTRIES_AE,
    MAX_ENTRIES_HP, MAX_ENTRIES_VDA, MAX_ENTRIES_CG
)

def init_personal_vars(vars_dict, traced_fn):
    personal_info_fields = [
        "pan", "aadhaar", "name", "dob", "status", "emp_cat", "filing_status",
        "addr_flat", "addr_road", "addr_area", "addr_city", "addr_state", "addr_pin",
        "addr2_flat", "addr2_road", "addr2_area", "addr2_city", "addr2_state", "addr2_pin",
        "email", "mobile", "email2", "mobile2", "capacity", "verification_place", "verifier_pan",
        "refund_credit_flag", "rep_name", "rep_email", "rep_mobile", "iea_ack", "iea_date",
        "rep_assessee", "is_revised_after_dec31", "return_filing_date", "months_234b",
        "aadhaar_link_status", "passport",
    ]
    for field in personal_info_fields:
        default_value = "Linked" if field == "aadhaar_link_status" else ""
        vars_dict[field] = ctk.StringVar(value=default_value)
    for flag in ["has_foreign_assets", "is_director", "has_unlisted_equity"]:
        vars_dict[flag] = traced_fn(flag, "0")

def init_income_vars(vars_dict, traced_fn, selected_itr_type):
    summary_metrics = [
        "sal_gross", "sal_perks", "sal_profits", "sal_allowance", "sal_ent", "sal_ptax",
        "sal", "os_total", "hp_total", "bp_total", "stcg_sum", "ltcg_112a_sum",
        "vda_sum", "gti", "ded_total", "tti",
        "slab_tax", "rebate_87a", "ltcg_tax", "stcg_tax", "vda_tax", "winnings_tax",
        "surcharge", "cess", "interest_total", "late_fee_234f", "fee_234i",
        "tax_total", "it_total", "tax_net", "due_tax",
        "ae_total", "tb_total_dr", "tb_total_cr", "bs_assets_total", "bs_liab_total",
        "itr4_investments", "itr4_bank_balance", "buyback_price", "buyback_cost",
    ]
    for metric in summary_metrics:
        vars_dict[metric] = traced_fn(metric, "0")
    vars_dict["sal_std_ded"] = traced_fn("sal_std_ded", str(STD_DEDUCTION_NEW_REGIME))
    for field in ["sal_hra", "sal_lta"]:
        vars_dict[field] = traced_fn(field, "0")
    for metric in [
        "os_interest", "os_interest_it", "os_interest_other", "os_dividend",
        "os_dividend_foreign", "os_pension", "os_family_pension_ded", "os_winnings",
        "os_other", "os_interest_concessional", "os_gift", "ei_agri", "ei_div", "ei_other",
    ]:
        vars_dict[metric] = traced_fn(metric, "0")
    for field in ["div_q1_jun15", "div_q2_sep15", "div_q3_dec15", "div_q4_mar15", "div_q5_mar31"]:
        vars_dict[field] = traced_fn(field, "0")
    relief_val = traced_fn("relief_89a", "0") if selected_itr_type not in ["ITR-1", "ITR-4"] else ctk.StringVar(value="0")
    vars_dict["relief_89a"] = relief_val
    vars_dict["has_89a_relief"] = traced_fn("has_89a_relief", "No") if selected_itr_type not in ["ITR-1", "ITR-4"] else ctk.StringVar(value="No")

def init_business_vars(vars_dict, traced_fn):
    vars_dict["bp_nature"] = ctk.StringVar(value="")
    vars_dict["bp_presumptive"] = traced_fn("bp_presumptive", "0")
    for field in [
        "bp_cap", "bp_loans", "bp_creditors", "bp_inv", "bp_debtors", "bp_cash",
        "bp_opening_stock", "bp_depr", "bp_bad_debts", "msme_43b_disallowance",
        "msme_interest_disallowance", "bp_total_manual",
        "liab_cap_open", "liab_cap_close", "liab_cap_var",
        "liab_loan_open", "liab_loan_close", "liab_loan_var",
        "liab_cred_open", "liab_cred_close", "liab_cred_var",
        "liab_other_open", "liab_other_close", "liab_other_var",
        "ast_fixed_open", "ast_fixed_close", "ast_fixed_var",
        "ast_inv_open", "ast_inv_close", "ast_inv_var",
        "ast_debt_open", "ast_debt_close", "ast_debt_var",
        "ast_cash_open", "ast_cash_close", "ast_cash_var",
        "ast_other_open", "ast_other_close", "ast_other_var",
    ]:
        vars_dict[field] = traced_fn(field, "0")
    for key in ["tb_sales", "tb_purchases", "tb_direct_exp", "tb_indirect_exp", "tb_closing_stock"]:
        vars_dict[key] = traced_fn(key, "0")
    for key in [
        "bs_cap", "bs_res", "bs_loans", "bs_creditors", "bs_od", "bs_prov_tax",
        "bs_land", "bs_plant", "bs_furn", "bs_debtors", "bs_inv", "bs_cash", "bs_bank",
        "bs_loan_given", "bs_invmt",
    ]:
        vars_dict[key] = traced_fn(key, "0")
    for i in range(MAX_ENTRIES_44AD):
        for f in ["name", "nature"]: vars_dict[f"ad_{i}_{f}"] = ctk.StringVar(value="")
        for f in ["turnover", "digital", "inc_44ad"]: vars_dict[f"ad_{i}_{f}"] = traced_fn(f"ad_{i}_{f}", "0")
    for i in range(MAX_ENTRIES_44ADA):
        vars_dict[f"ada_{i}_name"] = ctk.StringVar(value="")
        for f in ["gross", "inc_44ada"]: vars_dict[f"ada_{i}_{f}"] = traced_fn(f"ada_{i}_{f}", "0")
    for i in range(MAX_BUSINESS_ENTITIES):
        vars_dict[f"gst_{i}_no"] = ctk.StringVar(value="")
        for f in ["turnover", "income", "var"]: vars_dict[f"gst_{i}_{f}"] = traced_fn(f"gst_{i}_{f}", "0")
    vars_dict["gst_applicable"] = ctk.StringVar(value="No")
    vars_dict["gst_number"] = ctk.StringVar(value="")
    vars_dict["gst_turnover"] = traced_fn("gst_turnover", "0")
    vars_dict["cash_txn_slab"] = ctk.StringVar(value="<= 5%")

def init_tax_deduction_vars(vars_dict, traced_fn):
    for field in [
        "ded_80ccd2", "ded_80ccd1b", "ded_80c", "ded_80d", "ded_80e",
        "ded_80tta", "ded_80ttb", "ded_80jjaa", "ded_80cch", "ded_80ggc",
    ]:
        vars_dict[field] = traced_fn(field, "0")
    vars_dict["ded_80ggc_party_pan"] = ctk.StringVar(value="")
    vars_dict["ded_80ggc_party_name"] = ctk.StringVar(value="")
    for i in range(5):
        vars_dict[f"ded_80g_{i}_amt"] = traced_fn(f"ded_80g_{i}_amt", "0")
        vars_dict[f"ded_80g_{i}_ifsc"] = ctk.StringVar(value="")
        vars_dict[f"ded_80g_{i}_ref"] = ctk.StringVar(value="")

def init_bank_vars(vars_dict, traced_fn):
    vars_dict["bank_ifsc"] = ctk.StringVar(value="")
    vars_dict["bank_acc"] = ctk.StringVar(value="")
    for i in range(MAX_ENTRIES_BANK):
        for f in ["ifsc", "acc", "name", "refund"]:
            vars_dict[f"bank_{i}_{f}"] = ctk.StringVar(value="" if f != "refund" else "No")

def init_disclosure_vars(vars_dict, traced_fn):
    for f in ["buyback_company", "buyback_acq_date", "buyback_date"]: vars_dict[f] = ctk.StringVar(value="")
    for f in ["buyback_shares", "buyback_cost", "buyback_price"]: vars_dict[f] = traced_fn(f, "0")
    for f in ["fa_category", "fa_entity", "fa_country", "fa_initial_val", "fa_peak_val"]:
        vars_dict[f] = ctk.StringVar(value="")

def init_schedule_vars(vars_dict, traced_fn):
    for i in range(MAX_ENTRIES_TDS):
        for f in ["tan", "name", "section", "cert", "date"]: vars_dict[f"tds_{i}_{f}"] = ctk.StringVar(value="")
        vars_dict[f"tds_{i}_amount"] = traced_fn(f"tds_{i}_amount", "0")
    for i in range(MAX_ENTRIES_TCS):
        for f in ["tan", "name", "section", "date"]: vars_dict[f"tcs_{i}_{f}"] = ctk.StringVar(value="")
        vars_dict[f"tcs_{i}_amount"] = traced_fn(f"tcs_{i}_amount", "0")
    for i in range(MAX_ENTRIES_TAX_PAID):
        for f in ["bsr", "challan", "date"]: vars_dict[f"tax_{i}_{f}"] = ctk.StringVar(value="")
        vars_dict[f"tax_{i}_amount"] = traced_fn(f"tax_{i}_amount", "0")
        vars_dict[f"tax_{i}_type"] = ctk.StringVar(value="Advance")
    for k in [
        "al_immovable", "al_movable", "al_liabilities",
        "cg_q1_jun15", "cg_q2_sep15", "cg_q3_dec15", "cg_q4_mar15", "cg_q5_mar31",
        "ltcg_112_input", "ltcg_112_exemption", "ltcg_prop_sale", "ltcg_prop_cost",
        "ltcg_prop_index_cost", "ltcg_prop_relief_amt",
    ]:
        vars_dict[k] = traced_fn(k, "0")
    for f in ["inc_gt_50l", "has_bp", "has_foreign", "has_unlisted", "has_agri_gt_5k"]:
        vars_dict[f] = traced_fn(f, "No")
    for i in range(MAX_ENTRIES_AE):
        vars_dict[f"ae_{i}_type"] = ctk.StringVar(value="")
        for f in ["reg", "tonnage", "months", "amount"]: vars_dict[f"ae_{i}_{f}"] = ctk.StringVar(value="")
    for i in range(MAX_ENTRIES_HP):
        for f in ["tenant", "address", "co_owner", "city", "state", "pin", "tenant_pan"]: vars_dict[f"hp_{i}_{f}"] = ctk.StringVar(value="")
        vars_dict[f"hp_{i}_muni_tax"] = ctk.StringVar(value="0")
        vars_dict[f"hp_{i}_type"] = ctk.StringVar(value="let-out")
        for f in ["net", "rent", "int_loan", "unrealised_rent"]: vars_dict[f"hp_{i}_{f}"] = traced_fn(f"hp_{i}_{f}", "0")
    for i in range(MAX_ENTRIES_VDA):
        for f in ["acq_date", "trans_date", "token", "type", "exchange"]: vars_dict[f"vda_{i}_{f}"] = ctk.StringVar(value="")
        for f in ["cost", "sale"]: vars_dict[f"vda_{i}_{f}"] = traced_fn(f"vda_{i}_{f}", "0")
    for i in range(MAX_ENTRIES_CG):
        for f in ["isin", "name"]: vars_dict[f"ltcg112a_{i}_{f}"] = ctk.StringVar(value="")
        for f in ["sale", "cost", "fmv", "gain"]: vars_dict[f"ltcg112a_{i}_{f}"] = traced_fn(f"ltcg112a_{i}_{f}", "0")
    for i in range(MAX_ENTRIES_CG):
        vars_dict[f"stcg_{i}_asset"] = ctk.StringVar(value="")
        for f in ["cost", "sale", "stcg"]: vars_dict[f"stcg_{i}_{f}"] = traced_fn(f"stcg_{i}_{f}", "0")
    for i in range(5):
        vars_dict[f"fa_{i}_country"] = vars_dict[f"fa_{i}_nature"] = ctk.StringVar(value="")
        vars_dict[f"fa_{i}_value"] = traced_fn(f"fa_{i}_value", "0")
    vars_dict["ltcg_prop_acq_date"] = ctk.StringVar(value="")
    for f in ["maintains_books", "bank_balance_31_03", "vda_total_gains", "vda_tds_194s", "tax_credits"]:
        vars_dict[f] = traced_fn(f, "0")

def initialize_all_vars(vars_dict, traced_fn, itr_type):
    init_personal_vars(vars_dict, traced_fn)
    init_income_vars(vars_dict, traced_fn, itr_type)
    init_business_vars(vars_dict, traced_fn)
    init_tax_deduction_vars(vars_dict, traced_fn)
    init_bank_vars(vars_dict, traced_fn)
    init_disclosure_vars(vars_dict, traced_fn)
    init_schedule_vars(vars_dict, traced_fn)
