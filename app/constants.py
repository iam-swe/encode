"""
Constants for the Encode therapy system.
"""

from typing import Final

ORCHESTRATOR_NAME: Final[str] = "orchestrator_agent"
POSITIVE_AGENT_NAME: Final[str] = "positive_agent"
NEUTRAL_AGENT_NAME: Final[str] = "neutral_agent"
NEGATIVE_AGENT_NAME: Final[str] = "negative_agent"
PROBLEM_SOLVER_NAME: Final[str] = "problem_solver_agent"
GUARDRAILS_AGENT_NAME: Final[str] = "guardrails_agent"
SYNTHESIZER_AGENT_NAME: Final[str] = "synthesizer_agent"

MULTI_AGENT_WORKFLOW_NAME: Final[str] = "multi_agent_workflow"

MOOD_POSITIVE: Final[str] = "positive"
MOOD_NEUTRAL: Final[str] = "neutral"
MOOD_NEGATIVE: Final[str] = "negative"
MOOD_UNKNOWN: Final[str] = "unknown"

INTENT_TALK: Final[str] = "talk"
INTENT_SOLUTION: Final[str] = "solution"
INTENT_UNKNOWN: Final[str] = "unknown"

PHASE_GREETING: Final[str] = "greeting"
PHASE_MOOD_CHECK: Final[str] = "mood_check"
PHASE_INTENT_CHECK: Final[str] = "intent_check"
PHASE_THERAPY: Final[str] = "therapy"
PHASE_SOLUTION: Final[str] = "solution"
PHASE_CLOSING: Final[str] = "closing"

CRISIS_RESOURCES = {
    "suicide_lifeline": "988 Suicide & Crisis Lifeline (call or text 988)",
    "crisis_text": "Crisis Text Line: Text HOME to 741741",
    "iasp": "International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/",
}
