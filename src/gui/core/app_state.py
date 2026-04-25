import customtkinter as ctk
from src.services.logging_service import log as logger

_KNOWN_KEYS = set()


class VarDict(dict):
    @classmethod
    def register_keys(cls, keys):
        _KNOWN_KEYS.update(keys)

    def __missing__(self, key):
        if _KNOWN_KEYS and key not in _KNOWN_KEYS:
            logger.warning(
                f"⚠️ VarDict: Accessing unregistered key '{key}' — possible typo"
            )
        self[key] = ctk.StringVar(value="")
        return self[key]
