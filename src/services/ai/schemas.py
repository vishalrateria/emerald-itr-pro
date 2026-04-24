FORM_16_SCHEMA = {
    "type": "object",
    "properties": {
        "sal_gross": {
            "type": ["integer", "null"],
            "description": "Gross Salary from Form 16"
        },
        "sal_perks": {
            "type": ["integer", "null"],
            "description": "Value of Perquisites"
        },
        "ded_16ia": {
            "type": ["integer", "null"],
            "description": "Standard Deduction u/s 16(ia)"
        },
        "confidence": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": "AI self-assessed accuracy score (0.0 to 1.0)"
        }
    },
    "required": ["sal_gross", "sal_perks", "ded_16ia", "confidence"]
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
                    "maxItems": 4
                },
                "total_income": {"type": "integer"}
            }
        },
        "deductions": {
            "type": "object",
            "properties": {
                "ded_16ia": {"type": "integer"}
            }
        },
        "schedules": {
            "type": "object",
            "properties": {
                "schedule_al_populated": {"type": "boolean"}
            }
        }
    }
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
                    "legal_ref": {"type": "string"}
                }
            }
        },
        "confidence": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0
        }
    },
    "required": ["warnings", "confidence"]
}

def validate_extraction_result(result: dict) -> tuple[bool, list]:
    """
    Validates AI extraction result against Form 16 schema.
    
    Args:
        result: Dict returned by AI
    
    Returns:
        (is_valid, error_list)
    """
    errors = []
    
    required_fields = ["sal_gross", "sal_perks", "ded_16ia", "confidence"]
    for field in required_fields:
        if field not in result:
            errors.append(f"Missing required field: {field}")
    
    if "confidence" in result:
        conf = result["confidence"]
        if not isinstance(conf, (int, float)) or conf < 0.0 or conf > 1.0:
            errors.append(f"Invalid confidence score: {conf}")
    
    for field in ["sal_gross", "sal_perks", "ded_16ia"]:
        if field in result and result[field] is not None:
            if not isinstance(result[field], int):
                errors.append(f"{field} must be integer or null")
    
    return len(errors) == 0, errors

def validate_audit_result(result: dict) -> tuple[bool, list]:
    """
    Validates AI audit result against warning schema.

    Args:
        result: Dict returned by AI

    Returns:
        (is_valid, error_list)
    """
    errors = []

    if "warnings" not in result:
        errors.append("Missing 'warnings' field")
    elif not isinstance(result["warnings"], list):
        errors.append("'warnings' must be an array")

    if "confidence" in result:
        conf = result["confidence"]
        if not isinstance(conf, (int, float)) or conf < 0.0 or conf > 1.0:
            errors.append(f"Invalid confidence score: {conf}")

    return len(errors) == 0, errors


# ============================================
# NEW SCHEMAS FOR EXTENDED AI CAPABILITIES
# ============================================

FORM_26AS_SCHEMA = {
    "type": "object",
    "properties": {
        "tan": {"type": ["string", "null"], "description": "Tax Deduction Account Number"},
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
                    "quarter": {"type": "string"}
                }
            }
        },
        "total_tds": {"type": ["integer", "null"], "description": "Total TDS deducted"},
        "total_claim": {"type": ["integer", "null"], "description": "Total TDS claimed"},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0}
    },
    "required": ["total_tds", "confidence"]
}

AIS_SCHEMA = {
    "type": "object",
    "properties": {
        "pan": {"type": ["string", "null"], "description": "PAN from AIS"},
        "name": {"type": ["string", "null"], "description": "Name from AIS"},
        "financial_year": {"type": ["string", "null"]},
        "salary_income": {"type": ["integer", "null"], "description": "Total salary as per AIS"},
        "interest_income": {"type": ["integer", "null"], "description": "Total interest income"},
        "other_income": {"type": ["integer", "null"], "description": "Other income"},
        "tds_details": {
            "type": ["array", "null"],
            "items": {
                "type": "object",
                "properties": {
                    "source": {"type": "string"},
                    "amount": {"type": "integer"},
                    "tax_deducted": {"type": "integer"}
                }
            }
        },
        "total_income": {"type": ["integer", "null"]},
        "total_tds": {"type": ["integer", "null"]},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0}
    },
    "required": ["total_income", "confidence"]
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
                    "eligibility": {"type": "string", "enum": ["Eligible", "Partial", "Not Eligible"]}
                }
            }
        },
        "regime_comparison": {
            "type": "object",
            "properties": {
                "new_regime_tax": {"type": "integer"},
                "old_regime_tax": {"type": "integer"},
                "recommendation": {"type": "string"}
            }
        },
        "compliance_alerts": {
            "type": "array",
            "items": {"type": "string"}
        },
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0}
    },
    "required": ["tax_savings_suggestions", "confidence"]
}

DOCUMENT_CLASSIFICATION_SCHEMA = {
    "type": "object",
    "properties": {
        "document_type": {
            "type": "string",
            "enum": ["Form16", "Form26AS", "AIS", "ITR", "Salary Slip", "Investment Proof", "Unknown"]
        },
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "extracted_fields": {"type": "object", "description": "Key fields found in document"}
    },
    "required": ["document_type", "confidence"]
}


def validate_form26as_result(result: dict) -> tuple[bool, list]:
    """Validate Form 26AS extraction result."""
    errors = []

    if "total_tds" not in result:
        errors.append("Missing 'total_tds' field")

    if "confidence" in result:
        conf = result["confidence"]
        if not isinstance(conf, (int, float)) or conf < 0.0 or conf > 1.0:
            errors.append(f"Invalid confidence score: {conf}")

    return len(errors) == 0, errors


def validate_ais_result(result: dict) -> tuple[bool, list]:
    """Validate AIS extraction result."""
    errors = []

    if "total_income" not in result:
        errors.append("Missing 'total_income' field")

    if "confidence" in result:
        conf = result["confidence"]
        if not isinstance(conf, (int, float)) or conf < 0.0 or conf > 1.0:
            errors.append(f"Invalid confidence score: {conf}")

    return len(errors) == 0, errors


def validate_tax_advisory_result(result: dict) -> tuple[bool, list]:
    """Validate tax advisory result."""
    errors = []

    if "tax_savings_suggestions" not in result:
        errors.append("Missing 'tax_savings_suggestions' field")
    elif not isinstance(result["tax_savings_suggestions"], list):
        errors.append("'tax_savings_suggestions' must be an array")

    if "confidence" in result:
        conf = result["confidence"]
        if not isinstance(conf, (int, float)) or conf < 0.0 or conf > 1.0:
            errors.append(f"Invalid confidence score: {conf}")

    return len(errors) == 0, errors


def validate_classification_result(result: dict) -> tuple[bool, list]:
    """Validate document classification result."""
    errors = []

    if "document_type" not in result:
        errors.append("Missing 'document_type' field")

    valid_types = ["Form16", "Form26AS", "AIS", "ITR", "Salary Slip", "Investment Proof", "Unknown"]
    if "document_type" in result and result["document_type"] not in valid_types:
        errors.append(f"Invalid document_type. Must be one of: {valid_types}")

    if "confidence" in result:
        conf = result["confidence"]
        if not isinstance(conf, (int, float)) or conf < 0.0 or conf > 1.0:
            errors.append(f"Invalid confidence score: {conf}")

    return len(errors) == 0, errors
