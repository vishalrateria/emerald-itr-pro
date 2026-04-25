import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Callable, Optional
from src.services.logging_service import log as logger

try:
    import llama_cpp

    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False
from .hardware_utils import (
    get_hardware_profile,
    get_hardware_config,
    sanitize_pii,
    truncate_for_context,
)
from .prompts import (
    get_extraction_prompt,
    get_audit_prompt,
    get_form16_schema_json,
    get_form26as_prompt,
    get_form26as_schema_json,
    get_ais_prompt,
    get_ais_schema_json,
    get_tax_advisory_prompt,
    get_tax_advisory_schema_json,
    get_classify_prompt,
    get_classification_schema_json,
)
from .schemas import (
    validate_extraction_result,
    validate_audit_result,
    validate_form26as_result,
    validate_ais_result,
    validate_tax_advisory_result,
    validate_classification_result,
    FORM_16_SCHEMA,
    FORM_26AS_SCHEMA,
    AIS_SCHEMA,
    TAX_ADVISORY_SCHEMA,
    DOCUMENT_CLASSIFICATION_SCHEMA,
)

CONF_THRESHOLD = 0.85


class AIManager:
    _instance = None
    _initialized = False

    def __new__(cls, model_path: str = None, profile: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, model_path: str = None, profile: str = None):
        if AIManager._initialized:
            return
        if model_path is None:
            model_path = self._get_default_model_path()
        if profile is None:
            profile = get_hardware_profile()
        self.model_path = model_path
        self.profile = profile
        self.llm = None
        self.hw_config = get_hardware_config(profile)
        self._model_available = self._check_model_availability()
        from src.services.settings_service import SettingsManager

        pool_size = SettingsManager.get("AI.thread_pool_size", 1)
        self.executor = ThreadPoolExecutor(max_workers=pool_size)
        AIManager._initialized = True
        logger.info(
            f"AIManager initialized with profile: {profile}, model available: {self._model_available}"
        )

    def _check_model_availability(self) -> bool:
        if not LLAMA_CPP_AVAILABLE:
            logger.info("LLAMA_CPP_AVAILABLE is False - AI features disabled")
            return False
        if not os.path.exists(self.model_path):
            logger.warning(
                f"Model file not found at {self.model_path} - AI features disabled"
            )
            return False
        return True

    def is_available(self) -> bool:
        from src.services.settings_service import SettingsManager

        user_enabled = SettingsManager.get("AI.enabled", True)
        return (
            self._model_available
            and self.hw_config.get("ai_enabled", False)
            and user_enabled
        )

    def get_status(self) -> dict:
        return {
            "available": self.is_available(),
            "model_available": self._model_available,
            "llama_cpp_available": LLAMA_CPP_AVAILABLE,
            "model_path": self.model_path if self._model_available else None,
            "profile": self.profile,
            "reason": self._get_unavailable_reason(),
        }

    def _get_unavailable_reason(self) -> str:
        if not LLAMA_CPP_AVAILABLE:
            return "llama-cpp-python not installed"
        if not self._model_available:
            return f"Model file not found at {self.model_path}"
        if not self.hw_config.get("ai_enabled", False):
            return "AI disabled in settings"
        return "Unknown"

    def _get_default_model_path(self) -> str:
        from src.services.settings_service import SettingsManager

        try:
            val = SettingsManager.get("AI.model_path")
            if val and os.path.exists(val):
                return val
        except Exception as e:
            logger.warning(f"Failed to read settings: {e}")

        models_dir = "models"
        if not os.path.exists(models_dir):
            os.makedirs(models_dir, exist_ok=True)
            return os.path.join(models_dir, "phi-4-mini-instruct-q4_k_m.gguf")

        all_models = [f for f in os.listdir(models_dir) if f.endswith(".gguf")]

        if not all_models:
            return os.path.join(models_dir, "phi-4-mini-instruct-q4_k_m.gguf")

        for f in all_models:
            if "phi" in f.lower():
                return os.path.join(models_dir, f)

        logger.info(f"Preferred model not found, using alternative: {all_models[0]}")
        return os.path.join(models_dir, all_models[0])

    def load_model(self):
        if self.llm is not None:
            return
        if not LLAMA_CPP_AVAILABLE:
            logger.error("llama-cpp-python not installed")
            raise ImportError("llama-cpp-python >= 0.3.1 required")
        if not os.path.exists(self.model_path):
            logger.error(f"Model file not found: {self.model_path}")
            self._disable_ai_in_settings()
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        try:
            logger.info(f"Loading model from {self.model_path}")
            self.llm = llama_cpp.Llama(
                model_path=self.model_path,
                n_ctx=self.hw_config["n_ctx"],
                n_gpu_layers=self.hw_config["n_gpu_layers"],
                n_threads=self.hw_config["n_threads"],
                verbose=False,
            )
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self._disable_ai_in_settings()
            raise

    def _disable_ai_in_settings(self):
        from src.services.settings_service import SettingsManager

        try:
            SettingsManager.set("AI.enabled", False)
            logger.info("Disabled AI via SettingsManager")
        except Exception as e:
            logger.warning(f"Failed to update settings: {e}")

    def _parse_json_response(self, response: str) -> dict:
        response = response.strip()
        decoder = json.JSONDecoder()
        pos = 0
        while pos < len(response):
            start = response.find("{", pos)
            if start == -1:
                break
            try:
                obj, end = decoder.raw_decode(response[start:])
                if isinstance(obj, dict):
                    return obj
            except json.JSONDecodeError:
                pass
            pos = start + 1
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON response: {response[:200]}")
            return None

    def _run_extraction(self, text: str) -> dict:
        try:
            self.load_model()
            text = sanitize_pii(text)
            text = truncate_for_context(text, self.hw_config["n_ctx"])
            schema_json = get_form16_schema_json()
            messages = get_extraction_prompt(text, schema_json)
            response = self.llm.create_chat_completion(
                messages=messages,
                temperature=0.1,
                max_tokens=512,
                response_format={"type": "json_object"},
            )
            result = self._parse_json_response(
                response["choices"][0]["message"]["content"]
            )
            if result:
                is_valid, errors = validate_extraction_result(result)
                if not is_valid:
                    logger.warning(f"Validation errors: {errors}")
                    result = None
            return result
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return None

    def _run_audit(self, vardict: dict) -> dict:
        try:
            self.load_model()
            vardict_json = json.dumps(vardict)
            messages = get_audit_prompt(vardict_json)
            response = self.llm.create_chat_completion(
                messages=messages,
                temperature=0.1,
                max_tokens=1024,
                response_format={"type": "json_object"},
            )
            result = self._parse_json_response(
                response["choices"][0]["message"]["content"]
            )
            if result:
                is_valid, errors = validate_audit_result(result)
                if not is_valid:
                    logger.warning(f"Validation errors: {errors}")
                    result = None
            return result
        except Exception as e:
            logger.error(f"Audit failed: {e}")
            return None

    def extract_data_async(
        self,
        text: str,
        schema_type: str = "form16",
        callback: Callable[[dict], None] = None,
    ):
        if not self.is_available():
            logger.info(f"AI is not available: {self._get_unavailable_reason()}")
            if callback:
                callback(
                    {
                        "status": "unavailable",
                        "data": None,
                        "reason": self._get_unavailable_reason(),
                    }
                )
            return

        def run_task():
            try:
                if schema_type == "form16":
                    result = self._run_extraction(text)
                elif schema_type == "audit":
                    result = self._run_audit(text)
                else:
                    result = None
                if result and callback:
                    callback({"status": "success", "data": result})
                elif callback:
                    callback({"status": "error", "data": None})
            except Exception as e:
                logger.error(f"Async task failed: {e}")
                if callback:
                    callback({"status": "error", "data": None, "error": str(e)})

        self.executor.submit(run_task)

    def audit_vardict_async(
        self,
        vardict: dict,
        callback: Callable[[dict], None] = None,
    ):
        self.extract_data_async(
            text=vardict,
            schema_type="audit",
            callback=callback,
        )

    def is_enabled(self) -> bool:
        from src.services.settings_service import SettingsManager

        user_enabled = SettingsManager.get("AI.enabled", True)
        return self.hw_config.get("ai_enabled", False) and user_enabled

    def get_profile(self) -> str:
        return self.profile

    def get_confidence_threshold(self) -> float:
        from src.services.settings_service import SettingsManager

        return SettingsManager.get("AI.confidence_threshold", CONF_THRESHOLD)

    def _run_form26as_extraction(self, text: str) -> dict:
        try:
            self.load_model()
            text = sanitize_pii(text)
            text = truncate_for_context(text, self.hw_config["n_ctx"])
            schema_json = get_form26as_schema_json()
            messages = get_form26as_prompt(text, schema_json)
            response = self.llm.create_chat_completion(
                messages=messages,
                temperature=0.1,
                max_tokens=1024,
                response_format={"type": "json_object"},
            )
            result = self._parse_json_response(
                response["choices"][0]["message"]["content"]
            )
            if result:
                is_valid, errors = validate_form26as_result(result)
                if not is_valid:
                    logger.warning(f"Form26AS validation errors: {errors}")
                    result = None
            return result
        except Exception as e:
            logger.error(f"Form26AS extraction failed: {e}")
            return None

    def _run_ais_extraction(self, ais_json: str) -> dict:
        try:
            self.load_model()
            ais_json = sanitize_pii(ais_json)
            ais_json = truncate_for_context(ais_json, self.hw_config["n_ctx"])
            schema_json = get_ais_schema_json()
            messages = get_ais_prompt(ais_json, schema_json)
            response = self.llm.create_chat_completion(
                messages=messages,
                temperature=0.1,
                max_tokens=1024,
                response_format={"type": "json_object"},
            )
            result = self._parse_json_response(
                response["choices"][0]["message"]["content"]
            )
            if result:
                is_valid, errors = validate_ais_result(result)
                if not is_valid:
                    logger.warning(f"AIS validation errors: {errors}")
                    result = None
            return result
        except Exception as e:
            logger.error(f"AIS extraction failed: {e}")
            return None

    def _run_tax_advisory(self, vardict: dict) -> dict:
        try:
            self.load_model()
            vardict_json = json.dumps(vardict)
            messages = get_tax_advisory_prompt(vardict_json)
            response = self.llm.create_chat_completion(
                messages=messages,
                temperature=0.2,
                max_tokens=1536,
                response_format={"type": "json_object"},
            )
            result = self._parse_json_response(
                response["choices"][0]["message"]["content"]
            )
            if result:
                is_valid, errors = validate_tax_advisory_result(result)
                if not is_valid:
                    logger.warning(f"Tax Advisory validation errors: {errors}")
                    result = None
            return result
        except Exception as e:
            logger.error(f"Tax Advisory failed: {e}")
            return None

    def _run_classification(self, content: str) -> dict:
        try:
            self.load_model()
            content = sanitize_pii(content)
            messages = get_classify_prompt(content)
            response = self.llm.create_chat_completion(
                messages=messages,
                temperature=0.1,
                max_tokens=256,
                response_format={"type": "json_object"},
            )
            result = self._parse_json_response(
                response["choices"][0]["message"]["content"]
            )
            if result:
                is_valid, errors = validate_classification_result(result)
                if not is_valid:
                    logger.warning(f"Classification validation errors: {errors}")
                    result = None
            return result
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return None

    def extract_form26as_async(
        self, text: str, callback: Callable[[dict], None] = None
    ):
        if not self.is_available():
            logger.info(f"AI is not available: {self._get_unavailable_reason()}")
            if callback:
                callback(
                    {
                        "status": "unavailable",
                        "data": None,
                        "reason": self._get_unavailable_reason(),
                    }
                )
            return

        def run_task():
            try:
                result = self._run_form26as_extraction(text)
                if result and callback:
                    callback({"status": "success", "data": result})
                elif callback:
                    callback({"status": "error", "data": None})
            except Exception as e:
                logger.error(f"Form26AS async task failed: {e}")
                if callback:
                    callback({"status": "error", "data": None, "error": str(e)})

        self.executor.submit(run_task)

    def extract_ais_async(self, ais_json: str, callback: Callable[[dict], None] = None):
        if not self.is_available():
            logger.info(f"AI is not available: {self._get_unavailable_reason()}")
            if callback:
                callback(
                    {
                        "status": "unavailable",
                        "data": None,
                        "reason": self._get_unavailable_reason(),
                    }
                )
            return

        def run_task():
            try:
                result = self._run_ais_extraction(ais_json)
                if result and callback:
                    callback({"status": "success", "data": result})
                elif callback:
                    callback({"status": "error", "data": None})
            except Exception as e:
                logger.error(f"AIS async task failed: {e}")
                if callback:
                    callback({"status": "error", "data": None, "error": str(e)})

        self.executor.submit(run_task)

    def get_tax_advisory_async(
        self, vardict: dict, callback: Callable[[dict], None] = None
    ):
        if not self.is_available():
            logger.info(f"AI is not available: {self._get_unavailable_reason()}")
            if callback:
                callback(
                    {
                        "status": "unavailable",
                        "data": None,
                        "reason": self._get_unavailable_reason(),
                    }
                )
            return

        def run_task():
            try:
                result = self._run_tax_advisory(vardict)
                if result and callback:
                    callback({"status": "success", "data": result})
                elif callback:
                    callback({"status": "error", "data": None})
            except Exception as e:
                logger.error(f"Tax Advisory async task failed: {e}")
                if callback:
                    callback({"status": "error", "data": None, "error": str(e)})

        self.executor.submit(run_task)

    def classify_document_async(
        self, content: str, callback: Callable[[dict], None] = None
    ):
        if not self.is_available():
            logger.info(f"AI is not available: {self._get_unavailable_reason()}")
            if callback:
                callback(
                    {
                        "status": "unavailable",
                        "data": None,
                        "reason": self._get_unavailable_reason(),
                    }
                )
            return

        def run_task():
            try:
                result = self._run_classification(content)
                if result and callback:
                    callback({"status": "success", "data": result})
                elif callback:
                    callback({"status": "error", "data": None})
            except Exception as e:
                logger.error(f"Classification async task failed: {e}")
                if callback:
                    callback({"status": "error", "data": None, "error": str(e)})

        self.executor.submit(run_task)

    def cleanup(self):
        if self.llm:
            del self.llm
            self.llm = None
        self.executor.shutdown(wait=True)
        AIManager._initialized = False
        AIManager._instance = None
        logger.info("AIManager cleaned up")


def get_ai_manager() -> AIManager:
    return AIManager()


def log_audit_decision(
    field: str,
    ai_value: Any,
    final_value: Any,
    confidence: float,
    accepted: bool,
):
    log_path = os.path.join("data", "ai_audit_log.json")
    entry = {
        "timestamp": datetime.now().isoformat(),
        "field": field,
        "ai_value": ai_value,
        "final_value": final_value,
        "confidence": confidence,
        "accepted": accepted,
    }
    try:
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                logs = json.load(f)
        else:
            logs = []
        logs.append(entry)
        with open(log_path, "w") as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to log audit decision: {e}")
