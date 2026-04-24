def validate_tax_computation(vars_data: dict) -> bool:
    tti = float(vars_data.get("tti", 0) or 0)
    tax_total = float(vars_data.get("tax_total", 0) or 0)
    return tax_total >= 0 and tti >= 0
