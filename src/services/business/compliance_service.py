class ComplianceService:
    @staticmethod
    def run_compliance_checks(vars_data: dict) -> list:
        from src.core.engine import ITREngine
        gti = float(vars_data.get("gti", 0) or 0)
        tti = float(vars_data.get("tti", 0) or 0)
        due_tax = float(vars_data.get("due_tax", 0) or 0)
        itr_type = vars_data.get("itr_type", "ITR-4")
        return ITREngine.perform_audit_scan(vars_data, gti, tti, due_tax, itr_type)
