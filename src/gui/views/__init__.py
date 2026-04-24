from .dashboard.master_view import MasterSchedule
from .personal.personal_view import PersonalSchedule
from .income.deductions_view import DeductionsSchedule
from .disclosures.exempt_view import ExemptIncomeSchedule
from .verify.verify_view import VerifySchedule

from .income.salary_view import SalarySchedule
from .income.house_property_view import HousePropertySchedule
from .capital_gains.ltcg_view import LTCGSchedule
from .capital_gains.stcg_view import STCGSchedule
from .capital_gains.vda_view import VDASchedule
from .income.other_sources_view import OtherSourcesSchedule
from .disclosures.fa_view import ForeignAssetsSchedule

from .business.business_financials import BusinessFinancialsSchedule
from .business.presumptive_44ad import Presumptive44ADSchedule
from .business.presumptive_44ada import Presumptive44ADASchedule
from .business.presumptive_44ae import Presumptive44AESchedule
from .business.trial_balance import TrialBalanceSchedule
from .business.balance_sheet import BalanceSheetSchedule

from .audit.wizard_view import WizardSchedule
from .audit.audit_view import AuditSchedule

from .tax.tax_paid_view import TaxPaidSchedule

__all__ = [
    "MasterSchedule",
    "PersonalSchedule",
    "DeductionsSchedule",
    "ExemptIncomeSchedule",
    "VerifySchedule",
    "SalarySchedule",
    "HousePropertySchedule",
    "LTCGSchedule",
    "STCGSchedule",
    "VDASchedule",
    "OtherSourcesSchedule",
    "BusinessFinancialsSchedule",
    "Presumptive44ADSchedule",
    "Presumptive44ADASchedule",
    "Presumptive44AESchedule",
    "TrialBalanceSchedule",
    "BalanceSheetSchedule",
    "TaxPaidSchedule",
    "ForeignAssetsSchedule",
    "WizardSchedule",
    "AuditSchedule",
]
