"""
Mood and intent detection utilities.
"""

import os
from typing import Any

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI


def get_llm(temperature: float = 0.0) -> Any:
    """Get an LLM instance for detection tasks using Gemini 2.5 Flash."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Please set GOOGLE_API_KEY in your .env file")
    return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=temperature)


MOOD_DETECTOR_PROMPT = """Analyze the user's message and determine their emotional state.

User message: "{message}"

Classify as one of:
- positive: happy, excited, grateful, good, hopeful
- neutral: okay, fine, so-so, neither good nor bad
- negative: sad, anxious, stressed, overwhelmed, frustrated, upset

Output ONLY one word: positive, neutral, or negative"""


INTENT_DETECTOR_PROMPT = """Analyze if the user wants to talk/vent or wants solutions/advice.

User message: "{message}"

Classify as one of:
- talk: wants to express feelings, be heard, vent, discuss emotions
- solution: wants advice, solutions, practical help, steps to take

Output ONLY one word: talk or solution"""


def detect_mood(message: str) -> str:
    """Detect user mood from their message.

    Args:
        message: The user's message text

    Returns:
        One of: 'positive', 'neutral', 'negative', or 'unknown'
    """
    try:
        llm = get_llm(temperature=0)
        response = llm.invoke([
            HumanMessage(content=MOOD_DETECTOR_PROMPT.format(message=message))
        ])
        mood = response.content.strip().lower()
        if mood in ["positive", "neutral", "negative"]:
            return mood
        return "unknown"
    except Exception:
        return "unknown"


def detect_intent(message: str) -> str:
    """Detect user intent from their message.

    Args:
        message: The user's message text

    Returns:
        One of: 'talk', 'solution', or 'unknown'
    """
    try:
        llm = get_llm(temperature=0)
        response = llm.invoke([
            HumanMessage(content=INTENT_DETECTOR_PROMPT.format(message=message))
        ])
        intent = response.content.strip().lower()
        if intent in ["talk", "solution"]:
            return intent
        return "unknown"
    except Exception:
        return "unknown"
