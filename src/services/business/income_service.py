class IncomeService:
    @staticmethod
    def calculate_total_income(vars_data: dict) -> float:
        return float(vars_data.get("gti", 0) or 0)
