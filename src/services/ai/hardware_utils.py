import os
import re
from typing import Optional
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
from src.services.logging_service import log as logger
def get_available_memory_mb() -> float:
    if not PSUTIL_AVAILABLE:
        logger.warning("psutil not available - defaulting to Eco profile")
        return 0.0
    try:
        mem = psutil.virtual_memory()
        available_mb = mem.available / (1024 * 1024)
        return available_mb
    except Exception as e:
        logger.warning(f"Failed to get memory info: {e} - defaulting to Eco profile")
        return 0.0
def get_cpu_count() -> int:
    if not PSUTIL_AVAILABLE:
        return 1
    try:
        return psutil.cpu_count(logical=True) or 1
    except Exception:
        return 1
def get_hardware_profile() -> str:
    available_mb = get_available_memory_mb()
    available_gb = available_mb / 1024
    logger.info(f"Detected {available_gb:.1f}GB available RAM")
    if available_mb == 0.0:
        logger.warning("Hardware detection failed - defaulting to Eco profile")
        return 'eco'
    if available_gb < 4:
        logger.info("Hardware profile: Eco (< 4GB)")
        return 'eco'
    elif available_gb <= 12:
        logger.info("Hardware profile: Standard (4-12GB)")
        return 'standard'
    else:
        logger.info("Hardware profile: Pro (> 12GB)")
        return 'pro'
def get_hardware_config(profile: str) -> dict:
    cpu_count = get_cpu_count()
    configs = {
        'eco': {
            'n_ctx': 1024,
            'n_gpu_layers': 0,
            'n_threads': 1,
            'ai_enabled': False,
        },
        'standard': {
            'n_ctx': 2048,
            'n_gpu_layers': 0,
            'n_threads': max(1, cpu_count // 2),
            'ai_enabled': True,
        },
        'pro': {
            'n_ctx': 4096,
            'n_gpu_layers': min(35, cpu_count * 4),
            'n_threads': max(1, cpu_count - 1),
            'ai_enabled': True,
        },
    }
    return configs.get(profile, configs['eco'])
def sanitize_pii(text: str) -> str:
    text = re.sub(
        r'\b[A-Z]{5}([0-9]{4})[A-Z]{1}\b',
        r'XXXXX\1X',
        text
    )
    text = re.sub(
        r'\b\d{4}\s?\d{4}\s?(\d{4})\b',
        r'XXXX XXXX \1',
        text
    )
    return text
def truncate_for_context(text: str, max_tokens: int = 2048) -> str:
    max_chars = max_tokens * 4
    if len(text) <= max_chars:
        return text
    keep_length = max_chars // 2
    return text[:keep_length] + "\n\n[... content truncated for context ...]\n\n" + text[-keep_length:]