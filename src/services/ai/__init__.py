from .ai_manager import AIManager, get_ai_manager
from .hardware_utils import get_hardware_profile, get_available_memory_mb
from .prompts import get_extraction_prompt, get_audit_prompt, PROMPT_VERSION
from .schemas import (
    FORM_16_SCHEMA,
    VARDICT_SCHEMA,
    FORM_26AS_SCHEMA,
    AIS_SCHEMA,
    TAX_ADVISORY_SCHEMA,
    DOCUMENT_CLASSIFICATION_SCHEMA,
)

__all__ = [
    "AIManager",
    "get_ai_manager",
    "get_hardware_profile",
    "get_available_memory_mb",
    "get_extraction_prompt",
    "get_audit_prompt",
    "PROMPT_VERSION",
    "FORM_16_SCHEMA",
    "VARDICT_SCHEMA",
    "FORM_26AS_SCHEMA",
    "AIS_SCHEMA",
    "TAX_ADVISORY_SCHEMA",
    "DOCUMENT_CLASSIFICATION_SCHEMA",
]
