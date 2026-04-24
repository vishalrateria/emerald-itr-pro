import json
from typing import Dict, Any, List
from datetime import datetime
from src.services.logging_service import log as logger

def remove_empty_nodes(data):
    if isinstance(data, dict):
        return {k: remove_empty_nodes(v) for k, v in data.items() if v not in [{}, [], "", None]}
    elif isinstance(data, list):
        return [remove_empty_nodes(item) for item in data if item not in [{}, [], "", None]]
    return data

class ITRMapperService:
    @staticmethod
    def _val(v: Dict[str, Any], k: str) -> float:
        try:
            val = v.get(k).get() if hasattr(v.get(k), "get") else str(v.get(k, "0"))
            return float(val.replace(",", "")) if val else 0.0
        except Exception:
            return 0.0

    @staticmethod
    def _txt(v: Dict[str, Any], k: str, default: str = "") -> str:
        try:
            val = v.get(k).get() if hasattr(v.get(k), "get") else str(v.get(k, default))
            return val if val else default
        except Exception:
            return default

    @staticmethod
    def _sanitize(s: str) -> str:
        return "".join(c for c in str(s) if c.isalnum()).upper()

    @staticmethod
    def map_to_itr(form_type: str, v: Dict[str, Any]) -> Dict[str, Any]:
        try:
            form_key = form_type.replace("-", "")
            base = {
                "ITR": {
                    form_key: {
                        "CreationInfo": {
                            "SWVersionNo": "1.0",
                            "SWCreatedBy": "Emerald ITR Pro",
                            "XMLCreatedBy": "Emerald ITR Pro",
                            "XMLCreationDate": datetime.now().strftime("%Y-%m-%d"),
                        },
                        f"Form_{form_key}": {
                            "FormName": form_type,
                            "Description": f"Income Tax Return {form_type}",
                            "AssessmentYear": "2026",
                            "SchemaVer": "Ver1.0",
                            "FormVer": "Ver1.0"
                        },
                        "PartA_GEN1": ITRMapperService._map_part_a(v),
                        "PartB_TI": ITRMapperService._map_part_b_ti(v),
                        "PartB_TTI": ITRMapperService._map_part_b_tti(v),
                        "Schedule_BA": ITRMapperService._map_bank_accounts(v),
                        "Schedule_TDS1": ITRMapperService._map_tds(v, section_filter=["192"]),
                        "Schedule_TDS2": ITRMapperService._map_tds(v, section_filter=["194"]),
                        "Schedule_TCS": ITRMapperService._map_tcs(v),
                        "Schedule_IT": ITRMapperService._map_advance_tax(v),
                        "Verification": ITRMapperService._map_verification(v)
                    }
                }
            }
            
            if form_key in ["ITR2", "ITR3", "ITR4"]:
                base["ITR"][form_key]["Schedule_HP"] = ITRMapperService._map_hp(v)
                base["ITR"][form_key]["Schedule_BP"] = ITRMapperService._map_bp(v, form_key)
            if form_key in ["ITR2", "ITR3"]:
                base["ITR"][form_key]["Schedule_CG"] = ITRMapperService._map_cg(v)
                base["ITR"][form_key]["Schedule_VDA"] = ITRMapperService._map_vda(v)
                if ITRMapperService._txt(v, "has_foreign_assets", "0") in ["1", "yes", "true"]:
                    base["ITR"][form_key]["Schedule_FA"] = ITRMapperService._map_fa(v)
                
            if ITRMapperService._val(v, "tti") > 5000000 and form_key in ["ITR2", "ITR3", "ITR4"]:
                base["ITR"][form_key]["Schedule_AL"] = ITRMapperService._map_schedule_al(v)
                
            return remove_empty_nodes(base)
        except Exception as e:
            logger.error(f"ITR Mapping Error for {form_type}: {e}")
            return {}

    @staticmethod
    def _map_part_a(v: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "PersonalInfo": {
                "PAN": ITRMapperService._sanitize(ITRMapperService._txt(v, "pan")),
                "AssesseeName": {
                    "FirstName": ITRMapperService._txt(v, "name")
                },
                "DOB": ITRMapperService._txt(v, "dob")
            },
            "FilingStatus": {
                "ReturnFileSec": "139(1)",
                "NewTaxRegime": "Yes",
                "ResidentialStatus": "RES" if "non-resident" not in ITRMapperService._txt(v, "filing_status").lower() else "NRI"
            }
        }

    @staticmethod
    def _map_bank_accounts(v: Dict[str, Any]) -> Dict[str, Any]:
        accounts = []
        for i in range(5):
            acc_no = ITRMapperService._sanitize(ITRMapperService._txt(v, f"bank_{i}_acc"))
            if acc_no:
                accounts.append({
                    "BankAccountNo": acc_no,
                    "IFSCCode": ITRMapperService._sanitize(ITRMapperService._txt(v, f"bank_{i}_ifsc")),
                    "BankName": ITRMapperService._txt(v, f"bank_{i}_name"),
                    "UseForRefund": "Yes" if str(ITRMapperService._txt(v, f"bank_{i}_refund")).lower() in ["yes", "true", "1"] else "No"
                })
        return {"BankDetails": accounts}

    @staticmethod
    def _map_part_b_ti(v: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Salaries": {
                "GrossSalary": int(ITRMapperService._val(v, "sal_gross")),
                "StandardDeduction": int(ITRMapperService._val(v, "sal_std_ded")),
                "NetSalary": int(ITRMapperService._val(v, "sal"))
            },
            "HouseProperty": {"TotalHP": int(ITRMapperService._val(v, "hp_total"))},
            "OtherSources": {"TotalOS": int(ITRMapperService._val(v, "os_total"))},
            "GrossTotalIncome": int(ITRMapperService._val(v, "gti")),
            "ChapterVIA": {
                "Section80CCD2": int(ITRMapperService._val(v, "ded_80ccd2")),
                "Section80CCH": int(ITRMapperService._val(v, "ded_80cch")),
                "Section80JJAA": int(ITRMapperService._val(v, "ded_80jjaa")),
                "TotalDeductions": int(ITRMapperService._val(v, "ded_total"))
            },
            "TotalIncome": int(ITRMapperService._val(v, "tti"))
        }

    @staticmethod
    def _map_part_b_tti(v: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "TaxOnTotalIncome": int(ITRMapperService._val(v, "slab_tax")),
            "Rebate87A": int(ITRMapperService._val(v, "rebate_87a")),
            "Surcharge": int(ITRMapperService._val(v, "surcharge")),
            "HealthEducationCess": int(ITRMapperService._val(v, "cess")),
            "Relief89A": int(ITRMapperService._val(v, "relief_89a")),
            "TotalTaxLiability": int(ITRMapperService._val(v, "tax_total")),
            "Interest234A": int(ITRMapperService._val(v, "interest_234a")),
            "Interest234B": int(ITRMapperService._val(v, "interest_234b")),
            "Interest234C": int(ITRMapperService._val(v, "interest_234c")),
            "LateFee234F": int(ITRMapperService._val(v, "late_fee_234f")),
            "LateFee234I": int(ITRMapperService._val(v, "fee_234i")),
            "TotalTaxesPaid": int(ITRMapperService._val(v, "it_total")),
            "AmountPayable": int(ITRMapperService._val(v, "due_tax"))
        }

    @staticmethod
    def _map_tds(v: Dict[str, Any], section_filter: List[str]) -> List[Dict[str, Any]]:
        tds_list = []
        for i in range(10):
            amt = ITRMapperService._val(v, f"tds_{i}_amount")
            section = ITRMapperService._txt(v, f"tds_{i}_section")
            is_match = any(sec in section for sec in section_filter) if section else ("192" in section_filter)
            if amt > 0 and is_match:
                tds_list.append({
                    "TAN": ITRMapperService._sanitize(ITRMapperService._txt(v, f"tds_{i}_tan")),
                    "DeductorName": ITRMapperService._txt(v, f"tds_{i}_deductor"),
                    "Section": section,
                    "TotalTDS": int(amt)
                })
        return tds_list

    @staticmethod
    def _map_tcs(v: Dict[str, Any]) -> List[Dict[str, Any]]:
        tcs_list = []
        for i in range(10):
            amt = ITRMapperService._val(v, f"tcs_{i}_amount")
            if amt > 0:
                tcs_list.append({
                    "TAN": ITRMapperService._sanitize(ITRMapperService._txt(v, f"tcs_{i}_tan")),
                    "CollectorName": ITRMapperService._txt(v, f"tcs_{i}_collector"),
                    "TotalTCS": int(amt)
                })
        return tcs_list

    @staticmethod
    def _map_advance_tax(v: Dict[str, Any]) -> List[Dict[str, Any]]:
        adv_list = []
        for i in range(10):
            amt = ITRMapperService._val(v, f"tax_{i}_amount")
            if amt > 0:
                tax_type = "100" if "advance" in ITRMapperService._txt(v, f"tax_{i}_type").lower() else "300"
                adv_list.append({
                    "TaxType": tax_type,
                    "BSRCode": ITRMapperService._sanitize(ITRMapperService._txt(v, f"tax_{i}_bsr")),
                    "DateOfDeposit": ITRMapperService._txt(v, f"tax_{i}_date"),
                    "ChallanNo": ITRMapperService._sanitize(ITRMapperService._txt(v, f"tax_{i}_challan")),
                    "Amount": int(amt)
                })
        return adv_list

    @staticmethod
    def _map_hp(v: Dict[str, Any]) -> List[Dict[str, Any]]:
        hp_list = []
        for i in range(2):
            rent = ITRMapperService._val(v, f"hp_{i}_rent")
            if rent > 0 or ITRMapperService._txt(v, f"hp_{i}_type") == "self-occupied":
                hp_list.append({
                    "PropertyType": ITRMapperService._txt(v, f"hp_{i}_type").upper(),
                    "Address": {
                        "Street": ITRMapperService._txt(v, f"hp_{i}_address"),
                        "City": ITRMapperService._txt(v, f"hp_{i}_city"),
                        "State": ITRMapperService._txt(v, f"hp_{i}_state"),
                        "PinCode": ITRMapperService._txt(v, f"hp_{i}_pin")
                    },
                    "TenantDetails": {
                        "Name": ITRMapperService._txt(v, f"hp_{i}_tenant"),
                        "PAN": ITRMapperService._sanitize(ITRMapperService._txt(v, f"hp_{i}_tenant_pan"))
                    },
                    "GrossRent": int(rent),
                    "TaxesPaid": int(ITRMapperService._val(v, f"hp_{i}_muni_tax")),
                    "InterestOnBorrowedCapital": int(ITRMapperService._val(v, f"hp_{i}_int_loan"))
                })
        return hp_list

    @staticmethod
    def _map_schedule_al(v: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ImmovableProperty": int(ITRMapperService._val(v, "al_immovable")),
            "MovableProperty": int(ITRMapperService._val(v, "al_movable")),
            "FinancialAssets": int(ITRMapperService._val(v, "al_financial")),
            "VehiclesBullion": int(ITRMapperService._val(v, "al_bullion") + ITRMapperService._val(v, "al_vehicles")),
            "TotalLiabilities": int(ITRMapperService._val(v, "al_liabilities"))
        }

    @staticmethod
    def _map_bp(v: Dict[str, Any], form_key: str) -> Dict[str, Any]:
        bp_data = {"BusinessProfessionIncome": int(ITRMapperService._val(v, "bp_total"))}
        if form_key == "ITR4":
            sec44ad = []
            for i in range(5):
                turnover = ITRMapperService._val(v, f"ad_{i}_turnover")
                if turnover > 0:
                    sec44ad.append({
                        "BusinessCode": "09005",
                        "GrossTurnover": int(turnover),
                        "DigitalTurnover": int(ITRMapperService._val(v, f"ad_{i}_digital"))
                    })
            if sec44ad:
                bp_data["Sec44AD"] = sec44ad
                
            sec44ada = []
            for i in range(5):
                gross = ITRMapperService._val(v, f"ada_{i}_gross")
                if gross > 0:
                    sec44ada.append({
                        "ProfessionCode": "16019",
                        "GrossReceipts": int(gross)
                    })
            if sec44ada:
                bp_data["Sec44ADA"] = sec44ada
        return bp_data

    @staticmethod
    def _map_cg(v: Dict[str, Any]) -> Dict[str, Any]:
        cg_data = {
            "ShortTermCapitalGains": int(ITRMapperService._val(v, "stcg_sum")),
            "LongTermCapitalGains112": int(ITRMapperService._val(v, "ltcg_112_input"))
        }
        ltcg_112a_list = []
        for i in range(10):
            sale = ITRMapperService._val(v, f"ltcg112a_{i}_sale")
            if sale > 0:
                ltcg_112a_list.append({
                    "ISIN": ITRMapperService._sanitize(ITRMapperService._txt(v, f"ltcg112a_{i}_isin")),
                    "NameOfShare": ITRMapperService._txt(v, f"ltcg112a_{i}_name"),
                    "SalePricePerShare": int(sale),
                    "CostOfAcquisition": int(ITRMapperService._val(v, f"ltcg112a_{i}_cost")),
                    "FMVAsOn31Jan2018": int(ITRMapperService._val(v, f"ltcg112a_{i}_fmv")),
                    "TotalGain": int(ITRMapperService._val(v, f"ltcg112a_{i}_gain"))
                })
        if ltcg_112a_list:
            cg_data["Schedule112A"] = ltcg_112a_list
        return cg_data

    @staticmethod
    def _map_vda(v: Dict[str, Any]) -> Dict[str, Any]:
        vda_data = {"TotalVDAGains": int(ITRMapperService._val(v, "vda_sum"))}
        transactions = []
        for i in range(10):
            sale = ITRMapperService._val(v, f"vda_{i}_sale")
            if sale > 0:
                transactions.append({
                    "DateOfAcquisition": ITRMapperService._txt(v, f"vda_{i}_acq_date"),
                    "DateOfTransfer": ITRMapperService._txt(v, f"vda_{i}_trans_date"),
                    "HeadUnderWhichTaxed": "CapitalGains",
                    "CostOfAcquisition": int(ITRMapperService._val(v, f"vda_{i}_cost")),
                    "ConsiderationReceived": int(sale),
                    "IncomeFromVDA": int(max(0, sale - ITRMapperService._val(v, f"vda_{i}_cost")))
                })
        if transactions:
            vda_data["Transactions"] = transactions
        return vda_data

    @staticmethod
    def _map_fa(v: Dict[str, Any]) -> List[Dict[str, Any]]:
        fa_list = []
        for i in range(5):
            value = ITRMapperService._val(v, f"fa_{i}_value")
            if value > 0:
                fa_list.append({
                    "CountryCode": ITRMapperService._sanitize(ITRMapperService._txt(v, f"fa_{i}_country")),
                    "NatureOfAsset": ITRMapperService._txt(v, f"fa_{i}_nature"),
                    "PeakValueDuringYear": int(value)
                })
        return {"ForeignAssetsDetails": fa_list}

    @staticmethod
    def _map_verification(v: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Declaration": {
                "AssesseeVerName": ITRMapperService._txt(v, "name"),
                "FatherName": ITRMapperService._txt(v, "father_name", "Father"),
                "Capacity": ITRMapperService._txt(v, "capacity", "Self"),
                "VerificationPAN": ITRMapperService._sanitize(ITRMapperService._txt(v, "verifier_pan", ITRMapperService._txt(v, "pan"))),
                "Place": ITRMapperService._txt(v, "addr_city"),
                "Date": datetime.now().strftime("%Y-%m-%d")
            }
        }
