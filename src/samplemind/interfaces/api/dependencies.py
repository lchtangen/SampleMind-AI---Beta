"""Dependency injection for FastAPI"""

from typing import Any, Optional

# Global state storage (initialized in main.py lifespan)
_app_state = {}


def set_app_state(key: str, value: Any):
    """Set application state"""
    _app_state[key] = value


def get_app_state(key: str) -> Optional[Any]:
    """Get application state (for dependency injection)"""
    return _app_state.get(key)


def get_audio_engine():
    """Dependency: Get AudioEngine instance"""
    return get_app_state("audio_engine")


def get_ai_manager():
    """Dependency: Get AI Manager instance"""
    return get_app_state("ai_manager")
