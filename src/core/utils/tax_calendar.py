from datetime import datetime
from typing import List, Dict

class TaxCalendar:
    def __init__(self, assessment_year: str = "2026-27"):
        self.assessment_year = assessment_year
        self.fy_start = datetime(2025, 4, 1)
        self.fy_end = datetime(2026, 3, 31)

    def get_advance_tax_installments(self) -> List[Dict]:
        return [
            {
                "name": "Advance Tax - Installment 1",
                "due_date": datetime(2025, 6, 15),
                "percentage": 15,
                "description": "15% of advance tax by June 15"
            },
            {
                "name": "Advance Tax - Installment 2",
                "due_date": datetime(2025, 9, 15),
                "percentage": 45,
                "description": "45% of advance tax by September 15"
            },
            {
                "name": "Advance Tax - Installment 3",
                "due_date": datetime(2025, 12, 15),
                "percentage": 75,
                "description": "75% of advance tax by December 15"
            },
            {
                "name": "Advance Tax - Final Installment",
                "due_date": datetime(2026, 3, 15),
                "percentage": 100,
                "description": "100% of advance tax by March 15"
            }
        ]

    def get_interest_deadlines(self) -> List[Dict]:
        return [
            {
                "name": "Section 234A - Late Filing",
                "due_date": datetime(2026, 7, 31),
                "description": "Interest for not filing return by due date"
            },
            {
                "name": "Section 234B - Default in Advance Tax",
                "due_date": datetime(2026, 7, 31),
                "description": "Interest for shortfall in advance tax payment"
            },
            {
                "name": "Section 234C - Default in Installments",
                "due_date": datetime(2026, 3, 15),
                "description": "Interest for deferment of advance tax installments"
            }
        ]

    def get_filing_deadlines(self) -> List[Dict]:
        return [
            {
                "name": "ITR Filing Due Date (Non-Audit)",
                "due_date": datetime(2026, 7, 31),
                "description": "Last date to file ITR for non-audit cases"
            },
            {
                "name": "ITR Filing Due Date (Audit)",
                "due_date": datetime(2026, 10, 31),
                "description": "Last date to file ITR for audit cases"
            },
            {
                "name": "Belated Filing",
                "due_date": datetime(2026, 12, 31),
                "description": "Last date for belated ITR filing"
            }
        ]

    def get_upcoming_deadlines(self, days_ahead: int = 30) -> List[Dict]:
        today = datetime.now()
        all_deadlines = []

        all_deadlines.extend(self.get_advance_tax_installments())
        all_deadlines.extend(self.get_interest_deadlines())
        all_deadlines.extend(self.get_filing_deadlines())

        upcoming = []
        for deadline in all_deadlines:
            due_date = deadline["due_date"]
            days_until = (due_date - today).days

            if 0 <= days_until <= days_ahead:
                deadline["days_until"] = days_until
                deadline["status"] = "upcoming"
                upcoming.append(deadline)
            elif days_until < 0 and days_until >= -7:
                deadline["days_until"] = days_until
                deadline["status"] = "overdue"
                upcoming.append(deadline)

        return sorted(upcoming, key=lambda x: x["days_until"])

    def get_all_deadlines(self) -> List[Dict]:
        all_deadlines = []
        all_deadlines.extend(self.get_advance_tax_installments())
        all_deadlines.extend(self.get_interest_deadlines())
        all_deadlines.extend(self.get_filing_deadlines())
        return sorted(all_deadlines, key=lambda x: x["due_date"])
