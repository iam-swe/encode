"""
Centralized model definitions for AI agents.
Single source of truth for all model names used across the application.
"""

from typing import Final


class LLMModels:
    """Model name constants used across all agents."""

    # Google Models (primary)
    GEMINI_2_5_FLASH: Final[str] = "gemini-2.5-flash"
    GEMINI_2_5_PRO: Final[str] = "gemini-2.5-pro"
    GEMINI_2_0_FLASH: Final[str] = "gemini-2.0-flash"

    # Default model
    DEFAULT: Final[str] = GEMINI_2_5_FLASH
