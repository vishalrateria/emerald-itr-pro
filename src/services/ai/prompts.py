PROMPT_VERSION = "1.0"

SYSTEM_PROMPT_EXTRACTION = """You are a specialized Indian Tax Data Extractor. Your task is to convert unstructured text from "Form 16" into a valid JSON object matching the provided schema."""

SYSTEM_PROMPT_AUDIT = """You are a Senior Statutory Auditor for the Income Tax Department of India. Analyze the provided tax return data (VarDict) for internal contradictions based on the New Tax Regime (FY 25-26)."""

USER_PROMPT_EXTRACTION_TEMPLATE = """TEXT: {raw_text_sanitized}
SCHEMA: {form_16_schema}

INSTRUCTIONS:
1. Extract 'sal_gross' (Gross Salary), 'sal_perks' (Perquisites), and 'ded_16ia' (Standard Deduction).
2. Format numbers as integers (e.g., 500000). Remove commas.
3. Provide a 'confidence' score between 0.0 and 1.0 indicating your certainty.
4. If a field is not found, return `null`.
5. Output ONLY valid JSON, no markdown, no conversational text."""

USER_PROMPT_AUDIT_TEMPLATE = """DATA: {vardict_json}

CHECK FOR:
1. If 'sal_gross' > 0, is there a 'ded_16ia' of 75,000? (New Regime requirement).
2. If 'os_dividend' is reported, check if the 4-quarter breakdown matches for Section 234C.
3. If 'total_income' > 50,000,000, verify if 'schedule_al_populated' is true.

Output JSON with warnings if any discrepancies found. Include a 'confidence' score between 0.0 and 1.0."""

def get_extraction_prompt(raw_text: str, schema_json: str) -> list:
    """
    Returns formatted messages for extraction task.
    
    Args:
        raw_text: Sanitized text from document
        schema_json: JSON schema string
    
    Returns:
        List of message dicts for LLM
    """
    user_prompt = USER_PROMPT_EXTRACTION_TEMPLATE.format(
        raw_text_sanitized=raw_text,
        form_16_schema=schema_json
    )
    
    return [
        {"role": "system", "content": SYSTEM_PROMPT_EXTRACTION},
        {"role": "user", "content": user_prompt}
    ]

def get_audit_prompt(vardict_json: str) -> list:
    """
    Returns formatted messages for audit task.
    
    Args:
        vardict_json: VarDict state as JSON string
    
    Returns:
        List of message dicts for LLM
    """
    user_prompt = USER_PROMPT_AUDIT_TEMPLATE.format(
        vardict_json=vardict_json
    )
    
    return [
        {"role": "system", "content": SYSTEM_PROMPT_AUDIT},
        {"role": "user", "content": user_prompt}
    ]

def get_form16_schema_json() -> str:
    """Returns Form 16 schema as JSON string for prompt."""
    return """{
  "type": "object",
  "properties": {
    "sal_gross": { "type": ["integer", "null"], "description": "Gross Salary from Form 16" },
    "sal_perks": { "type": ["integer", "null"], "description": "Value of Perquisites" },
    "ded_16ia": { "type": ["integer", "null"], "description": "Standard Deduction u/s 16(ia)" },
    "confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0, "description": "AI self-assessed accuracy score (0.0 to 1.0)" }
  },
  "required": ["sal_gross", "sal_perks", "ded_16ia", "confidence"]
}"""


# ============================================
# NEW PROMPTS FOR EXTENDED AI CAPABILITIES
# ============================================

SYSTEM_PROMPT_FORM26AS = """You are a specialized Indian Tax Data Extractor. Extract TDS details from Form 26AS Annual Statement into valid JSON matching the schema."""

SYSTEM_PROMPT_AIS = """You are a specialized Indian Tax Data Extractor. Parse Annual Information Statement (AIS) JSON data and extract income details, TDS information, and other relevant fields."""

SYSTEM_PROMPT_TAX_ADVISORY = """You are a Senior Tax Consultant for India. Analyze the taxpayer's income details and provide tax-saving suggestions, regime comparison, and compliance alerts for FY 2025-26 (AY 2026-27)."""

SYSTEM_PROMPT_CLASSIFY = """You are a document classification AI. Analyze the provided text or document content and identify what type of Indian tax document it is."""

USER_PROMPT_FORM26AS_TEMPLATE = """FORM 26AS TEXT: {raw_text}
SCHEMA: {schema}

INSTRUCTIONS:
1. Extract TAN, deductor names, amounts claimed, TDS amounts, and quarters.
2. Calculate total_tds (sum of all TDS deducted).
3. Calculate total_claim (sum of all amounts claimed).
4. Provide a 'confidence' score between 0.0 and 1.0.
5. Output ONLY valid JSON, no markdown."""

USER_PROMPT_AIS_TEMPLATE = """AIS DATA: {ais_json}
SCHEMA: {schema}

INSTRUCTIONS:
1. Extract salary_income, interest_income, other_income from AIS.
2. Extract TDS details from all sources.
3. Calculate total_income and total_tds.
4. Provide a 'confidence' score between 0.0 and 1.0.
5. Output ONLY valid JSON, no markdown."""

USER_PROMPT_TAX_ADVISORY_TEMPLATE = """TAXPAYER DATA: {vardict_json}

INSTRUCTIONS:
1. Analyze the income details provided.
2. Provide tax_savings_suggestions with section, description, potential_savings, and eligibility.
3. Compare new vs old tax regime and provide regime_comparison.
4. List any compliance_alerts that need attention.
5. Provide a 'confidence' score between 0.0 and 1.0.
6. Output ONLY valid JSON, no markdown."""

USER_PROMPT_CLASSIFY_TEMPLATE = """DOCUMENT CONTENT: {content}

INSTRUCTIONS:
1. Analyze the document content and identify the document type.
2. Choose from: Form16, Form26AS, AIS, ITR, Salary Slip, Investment Proof, Unknown
3. Extract any key fields found (e.g., PAN, name, amounts).
4. Provide a 'confidence' score between 0.0 and 1.0.
5. Output ONLY valid JSON, no markdown."""


def get_form26as_prompt(raw_text: str, schema_json: str) -> list:
    """Returns formatted messages for Form 26AS extraction."""
    user_prompt = USER_PROMPT_FORM26AS_TEMPLATE.format(
        raw_text=raw_text,
        schema=schema_json
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT_FORM26AS},
        {"role": "user", "content": user_prompt}
    ]


def get_ais_prompt(ais_json: str, schema_json: str) -> list:
    """Returns formatted messages for AIS extraction."""
    user_prompt = USER_PROMPT_AIS_TEMPLATE.format(
        ais_json=ais_json,
        schema=schema_json
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT_AIS},
        {"role": "user", "content": user_prompt}
    ]


def get_tax_advisory_prompt(vardict_json: str) -> list:
    """Returns formatted messages for tax advisory."""
    user_prompt = USER_PROMPT_TAX_ADVISORY_TEMPLATE.format(
        vardict_json=vardict_json
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT_TAX_ADVISORY},
        {"role": "user", "content": user_prompt}
    ]


def get_classify_prompt(content: str) -> list:
    """Returns formatted messages for document classification."""
    user_prompt = USER_PROMPT_CLASSIFY_TEMPLATE.format(
        content=content[:5000]  # Limit content length
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT_CLASSIFY},
        {"role": "user", "content": user_prompt}
    ]


def get_form26as_schema_json() -> str:
    """Returns Form 26AS schema as JSON string."""
    return """{
  "type": "object",
  "properties": {
    "tan": { "type": ["string", "null"], "description": "Tax Deduction Account Number" },
    "assessee_name": { "type": ["string", "null"], "description": "Name as per TDS" },
    "financial_year": { "type": ["string", "null"], "description": "FY 2025-26" },
    "tds_details": { "type": ["array", "null"], "items": { "type": "object", "properties": { "tan": {"type": "string"}, "deductor_name": {"type": "string"}, "amount_claimed": {"type": "integer"}, "tds_amount": {"type": "integer"}, "quarter": {"type": "string"} } } },
    "total_tds": { "type": ["integer", "null"], "description": "Total TDS deducted" },
    "total_claim": { "type": ["integer", "null"], "description": "Total TDS claimed" },
    "confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 }
  },
  "required": ["total_tds", "confidence"]
}"""


def get_ais_schema_json() -> str:
    """Returns AIS schema as JSON string."""
    return """{
  "type": "object",
  "properties": {
    "pan": { "type": ["string", "null"], "description": "PAN from AIS" },
    "name": { "type": ["string", "null"], "description": "Name from AIS" },
    "financial_year": { "type": ["string", "null"] },
    "salary_income": { "type": ["integer", "null"], "description": "Total salary as per AIS" },
    "interest_income": { "type": ["integer", "null"], "description": "Total interest income" },
    "other_income": { "type": ["integer", "null"], "description": "Other income" },
    "tds_details": { "type": ["array", "null"], "items": { "type": "object", "properties": { "source": {"type": "string"}, "amount": {"type": "integer"}, "tax_deducted": {"type": "integer"} } } },
    "total_income": { "type": ["integer", "null"] },
    "total_tds": { "type": ["integer", "null"] },
    "confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 }
  },
  "required": ["total_income", "confidence"]
}"""


def get_tax_advisory_schema_json() -> str:
    """Returns Tax Advisory schema as JSON string."""
    return """{
  "type": "object",
  "properties": {
    "tax_savings_suggestions": { "type": "array", "items": { "type": "object", "properties": { "section": {"type": "string"}, "description": {"type": "string"}, "potential_savings": {"type": "integer"}, "eligibility": {"type": "string", "enum": ["Eligible", "Partial", "Not Eligible"]} } } },
    "regime_comparison": { "type": "object", "properties": { "new_regime_tax": {"type": "integer"}, "old_regime_tax": {"type": "integer"}, "recommendation": {"type": "string"} } },
    "compliance_alerts": { "type": "array", "items": {"type": "string"} },
    "confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 }
  },
  "required": ["tax_savings_suggestions", "confidence"]
}"""


def get_classification_schema_json() -> str:
    """Returns Document Classification schema as JSON string."""
    return """{
  "type": "object",
  "properties": {
    "document_type": { "type": "string", "enum": ["Form16", "Form26AS", "AIS", "ITR", "Salary Slip", "Investment Proof", "Unknown"] },
    "confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
    "extracted_fields": { "type": "object", "description": "Key fields found in document" }
  },
  "required": ["document_type", "confidence"]
}"""
