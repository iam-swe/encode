"""
State definition for the therapy agent workflow.
"""

from typing import Annotated, Any, Dict, List, Optional

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class TherapyState(TypedDict):
    """State shared across all nodes in the therapy workflow."""

    messages: Annotated[List[BaseMessage], add_messages]
    user_query: str
    user_mood: str
    user_intent: str
    phase: str
    session_summary: str
    turn_count: int
    current_response: Optional[str]
    guardrail_approved: bool
    error: List[str]
    orchestrator_result: Optional[Dict[str, Any]]


def get_conversation_context(state: TherapyState, max_messages: int = 6) -> str:
    """Build conversation context from message history."""
    from langchain_core.messages import AIMessage, HumanMessage

    context_parts: List[str] = []
    messages = state.get("messages", [])[-max_messages:]

    for msg in messages:
        if isinstance(msg, HumanMessage):
            context_parts.append(f"User: {msg.content}")
        elif isinstance(msg, AIMessage) and msg.content:
            if not getattr(msg, "tool_calls", None):
                content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                context_parts.append(f"Therapist: {content}")

    return "\n".join(context_parts)


def get_initial_state() -> TherapyState:
    """Get the initial therapy state."""
    return TherapyState(
        messages=[],
        user_query="",
        user_mood="unknown",
        user_intent="unknown",
        phase="greeting",
        session_summary="",
        turn_count=0,
        current_response=None,
        guardrail_approved=False,
        error=[],
        orchestrator_result=None,
    )
