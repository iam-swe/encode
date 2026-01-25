"""
Guardrails Node for the Therapy Workflow.
"""

from typing import Any, Dict

import structlog
from langchain_core.messages import AIMessage

from app.agents.guardrails_agent.guardrails_agent import GuardrailsAgent
from app.agents.state import TherapyState

logger = structlog.get_logger(__name__)


class GuardrailsNode:
    """Node for checking response safety through guardrails."""

    def __init__(self, guardrails_agent: GuardrailsAgent) -> None:
        self.guardrails_agent = guardrails_agent

    def process(self, state: TherapyState) -> Dict[str, Any]:
        """Process the current response through guardrails."""
        try:
            # Get latest AI response
            response_to_check = ""
            for msg in reversed(state.get("messages", [])):
                if isinstance(msg, AIMessage) and msg.content:
                    # Skip tool calls, get actual response
                    if not getattr(msg, "tool_calls", None):
                        response_to_check = msg.content
                        break

            if not response_to_check:
                return {"guardrail_approved": True}

            # Check through guardrails
            result = self.guardrails_agent.check_response_sync(response_to_check)
            checked_response = result.get("checked_response", response_to_check)

            # Update the last AI message with checked response
            new_messages = list(state.get("messages", []))
            for i in range(len(new_messages) - 1, -1, -1):
                if isinstance(new_messages[i], AIMessage) and not getattr(new_messages[i], "tool_calls", None):
                    new_messages[i] = AIMessage(content=checked_response)
                    break

            return {
                "messages": new_messages,
                "guardrail_approved": True,
                "current_response": checked_response,
            }

        except Exception as e:
            error_msg = f"Guardrails node failed: {str(e)}"
            logger.error("Guardrails node failed", error=str(e))
            return {
                "guardrail_approved": False,
                "error": [error_msg],
            }
