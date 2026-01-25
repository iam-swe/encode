"""
Orchestrator Node for the Therapy Workflow.
"""

from typing import Any, Dict

import structlog

from app.agents.base_agent import BaseAgent
from app.agents.state import TherapyState, get_conversation_context
from app.utils.mood_detector import detect_intent, detect_mood

logger = structlog.get_logger(__name__)


class OrchestratorNode:
    """Node for processing conversations through the orchestrator agent."""

    def __init__(self, orchestrator_agent: BaseAgent) -> None:
        self.orchestrator_agent = orchestrator_agent

    def process(self, state: TherapyState) -> Dict[str, Any]:
        """Process the current state through the orchestrator."""
        try:
            from langchain_core.messages import HumanMessage
            from langgraph.prebuilt import create_react_agent

            from app.tools.tool_registry import get_all_tools

            # Get latest user message
            user_msg = ""
            for msg in reversed(state.get("messages", [])):
                if isinstance(msg, HumanMessage):
                    user_msg = msg.content
                    break

            # Detect mood and intent if not set
            current_mood = state.get("user_mood", "unknown")
            current_intent = state.get("user_intent", "unknown")

            if current_mood == "unknown" and user_msg:
                current_mood = detect_mood(user_msg)

            if current_intent == "unknown" and user_msg:
                current_intent = detect_intent(user_msg)

            # Get conversation context
            context = get_conversation_context(state)

            # Get tools and create agent
            tools = get_all_tools()
            prompt = self.orchestrator_agent.get_prompt(state)

            agent = create_react_agent(
                self.orchestrator_agent.model,
                tools,
                prompt=prompt,
            )

            # Prepare state for orchestrator
            orch_state = {
                **state,
                "user_mood": current_mood,
                "user_intent": current_intent,
                "session_summary": context,
            }

            result = agent.invoke({"messages": state.get("messages", [])})

            return {
                "messages": result.get("messages", []),
                "user_mood": current_mood,
                "user_intent": current_intent,
                "orchestrator_result": result,
            }

        except Exception as e:
            error_msg = f"Orchestrator node failed: {str(e)}"
            logger.error("Orchestrator node failed", error=str(e))
            return {
                "orchestrator_result": None,
                "error": [error_msg],
            }
