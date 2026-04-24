from typing import Any, Dict, List, Union
import json
import os
from pathlib import Path
from src.services.logging_service import log as logger

def _deep_sanitize(obj: Any, key_context: str = "") -> Any:
    if isinstance(obj, dict):
        return {k: _deep_sanitize(v, k) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_deep_sanitize(item, key_context) for item in obj]
    elif isinstance(obj, str):
        cleaned = "".join(c for c in obj if c.isascii()).strip()
        upper_keys = ["PAN", "TAN", "GSTIN", "IFSC", "BSR", "ISIN"]
        if any(x in key_context.upper() for x in upper_keys) or key_context in [
            "TransactionId",
            "RegNo",
            "AckNo",
        ]:
            cleaned = cleaned.upper()
        return cleaned
    return obj

def safe_load_json(path: Union[str, Path]) -> Union[Dict, List, None]:
    ph = Path(path)
    if not ph.exists():
        return None
    try:
        with open(ph, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        logger.error(f"❌ Failed to load {ph}. Error: {e}")
        return None

def safe_save_json(path: Union[str, Path], data: Union[Dict, List]) -> bool:
    ph = Path(path)
    tmp = ph.with_suffix(".tmp")
    data = _deep_sanitize(data)
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        os.replace(tmp, ph)
        logger.info(f"💾 File successfully persisted at: {ph}")
        return True
    except Exception as e:
        logger.error(f"❌ CRITICAL I/O FAILURE: Failed to persist {ph}. Error: {e}")
        if tmp.exists():
            tmp.unlink()
        raise e
