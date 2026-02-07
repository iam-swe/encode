"""
Synthesizer Node for the Therapy Workflow.
"""

from typing import Any, Dict

import structlog
from langchain_core.messages import AIMessage

from app.agents.state import TherapyState
from app.agents.synthesizer_agent.synthesizer_agent import SynthesizerAgent

logger = structlog.get_logger(__name__)


class SynthesizerNode:
    """Node for synthesizing and polishing final responses."""

    def __init__(self, synthesizer_agent: SynthesizerAgent) -> None:
        self.synthesizer_agent = synthesizer_agent

    def process(self, state: TherapyState) -> Dict[str, Any]:
        """Process and polish the current response."""
        try:
            response_to_polish = state.get("current_response", "")

            if not response_to_polish:
                for msg in reversed(state.get("messages", [])):
                    if isinstance(msg, AIMessage) and msg.content:
                        if not getattr(msg, "tool_calls", None):
                            response_to_polish = msg.content
                            break

            if not response_to_polish:
                response_to_polish = "I'm here to listen. How are you feeling?"

            result = self.synthesizer_agent.synthesize_sync(response_to_polish)
            polished_response = result.get("polished_response", response_to_polish)

            new_messages = list(state.get("messages", []))
            for i in range(len(new_messages) - 1, -1, -1):
                if isinstance(new_messages[i], AIMessage) and not getattr(new_messages[i], "tool_calls", None):
                    new_messages[i] = AIMessage(content=polished_response)
                    break

            new_turn_count = state.get("turn_count", 0) + 1

            return {
                "messages": new_messages,
                "current_response": polished_response,
                "turn_count": new_turn_count,
            }

        except Exception as e:
            error_msg = f"Synthesizer node failed: {str(e)}"
            logger.error("Synthesizer node failed", error=str(e))
            return {
                "error": [error_msg],
            }
