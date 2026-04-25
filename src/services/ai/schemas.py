import jsonschema

FORM_16_SCHEMA = {
    "type": "object",
    "properties": {
        "sal_gross": {
            "type": ["integer", "null"],
            "description": "Gross Salary from Form 16",
        },
        "sal_perks": {
            "type": ["integer", "null"],
            "description": "Value of Perquisites",
        },
        "ded_16ia": {
            "type": ["integer", "null"],
            "description": "Standard Deduction u/s 16(ia)",
        },
        "confidence": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": "AI self-assessed accuracy score (0.0 to 1.0)",
        },
    },
    "required": ["sal_gross", "sal_perks", "ded_16ia", "confidence"],
}

VARDICT_SCHEMA = {
    "type": "object",
    "properties": {
        "income": {
            "type": "object",
            "properties": {
                "sal_gross": {"type": "integer"},
                "os_dividend": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "minItems": 4,
                    "maxItems": 4,
                },
                "total_income": {"type": "integer"},
            },
        },
        "deductions": {
            "type": "object",
            "properties": {"ded_16ia": {"type": "integer"}},
        },
        "schedules": {
            "type": "object",
            "properties": {"schedule_al_populated": {"type": "boolean"}},
        },
    },
}

AUDIT_WARNING_SCHEMA = {
    "type": "object",
    "properties": {
        "warnings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "severity": {"type": "string", "enum": ["Low", "Medium", "High"]},
                    "section": {"type": "string"},
                    "message": {"type": "string"},
                    "legal_ref": {"type": "string"},
                },
            },
        },
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
    },
    "required": ["warnings", "confidence"],
}


def validate_extraction_result(result: dict) -> tuple[bool, list]:
    try:
        jsonschema.validate(instance=result, schema=FORM_16_SCHEMA)
        return True, []
    except jsonschema.exceptions.ValidationError as e:
        return False, [str(e)]


def validate_audit_result(result: dict) -> tuple[bool, list]:
    try:
        jsonschema.validate(instance=result, schema=AUDIT_WARNING_SCHEMA)
        return True, []
    except jsonschema.exceptions.ValidationError as e:
        return False, [str(e)]


FORM_26AS_SCHEMA = {
    "type": "object",
    "properties": {
        "tan": {
            "type": ["string", "null"],
            "description": "Tax Deduction Account Number",
        },
        "assessee_name": {"type": ["string", "null"], "description": "Name as per TDS"},
        "financial_year": {"type": ["string", "null"], "description": "FY 2025-26"},
        "tds_details": {
            "type": ["array", "null"],
            "items": {
                "type": "object",
                "properties": {
                    "tan": {"type": "string"},
                    "deductor_name": {"type": "string"},
                    "amount_claimed": {"type": "integer"},
                    "tds_amount": {"type": "integer"},
                    "quarter": {"type": "string"},
                },
            },
        },
        "total_tds": {"type": ["integer", "null"], "description": "Total TDS deducted"},
        "total_claim": {
            "type": ["integer", "null"],
            "description": "Total TDS claimed",
        },
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
    },
    "required": ["total_tds", "confidence"],
}

AIS_SCHEMA = {
    "type": "object",
    "properties": {
        "pan": {"type": ["string", "null"], "description": "PAN from AIS"},
        "name": {"type": ["string", "null"], "description": "Name from AIS"},
        "financial_year": {"type": ["string", "null"]},
        "salary_income": {
            "type": ["integer", "null"],
            "description": "Total salary as per AIS",
        },
        "interest_income": {
            "type": ["integer", "null"],
            "description": "Total interest income",
        },
        "other_income": {"type": ["integer", "null"], "description": "Other income"},
        "tds_details": {
            "type": ["array", "null"],
            "items": {
                "type": "object",
                "properties": {
                    "source": {"type": "string"},
                    "amount": {"type": "integer"},
                    "tax_deducted": {"type": "integer"},
                },
            },
        },
        "total_income": {"type": ["integer", "null"]},
        "total_tds": {"type": ["integer", "null"]},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
    },
    "required": ["total_income", "confidence"],
}

TAX_ADVISORY_SCHEMA = {
    "type": "object",
    "properties": {
        "tax_savings_suggestions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "section": {"type": "string"},
                    "description": {"type": "string"},
                    "potential_savings": {"type": "integer"},
                    "eligibility": {
                        "type": "string",
                        "enum": ["Eligible", "Partial", "Not Eligible"],
                    },
                },
            },
        },
        "regime_comparison": {
            "type": "object",
            "properties": {
                "new_regime_tax": {"type": "integer"},
                "old_regime_tax": {"type": "integer"},
                "recommendation": {"type": "string"},
            },
        },
        "compliance_alerts": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
    },
    "required": ["tax_savings_suggestions", "confidence"],
}

DOCUMENT_CLASSIFICATION_SCHEMA = {
    "type": "object",
    "properties": {
        "document_type": {
            "type": "string",
            "enum": [
                "Form16",
                "Form26AS",
                "AIS",
                "ITR",
                "Salary Slip",
                "Investment Proof",
                "Unknown",
            ],
        },
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "extracted_fields": {
            "type": "object",
            "description": "Key fields found in document",
        },
    },
    "required": ["document_type", "confidence"],
}


def validate_form26as_result(result: dict) -> tuple[bool, list]:
    try:
        jsonschema.validate(instance=result, schema=FORM_26AS_SCHEMA)
        return True, []
    except jsonschema.exceptions.ValidationError as e:
        return False, [str(e)]


def validate_ais_result(result: dict) -> tuple[bool, list]:
    try:
        jsonschema.validate(instance=result, schema=AIS_SCHEMA)
        return True, []
    except jsonschema.exceptions.ValidationError as e:
        return False, [str(e)]


def validate_tax_advisory_result(result: dict) -> tuple[bool, list]:
    try:
        jsonschema.validate(instance=result, schema=TAX_ADVISORY_SCHEMA)
        return True, []
    except jsonschema.exceptions.ValidationError as e:
        return False, [str(e)]


def validate_classification_result(result: dict) -> tuple[bool, list]:
    try:
        jsonschema.validate(instance=result, schema=DOCUMENT_CLASSIFICATION_SCHEMA)
        return True, []
    except jsonschema.exceptions.ValidationError as e:
        return False, [str(e)]
