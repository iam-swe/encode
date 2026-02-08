"""
Agent tools for the multi-agent system.

These tools wrap the actual therapy agent instances so the orchestrator
delegates to them rather than duplicating agent logic inline.
"""

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import StructuredTool
from opik import track
from pydantic import BaseModel, Field


class TherapyInput(BaseModel):
    """Input schema for agent tools."""

    message: str = Field(description="The user's message to respond to")
    context: str = Field(description="Conversation context/summary", default="")


_agent_cache = {}


def _get_agent(agent_class):
    """Lazily instantiate and cache agent instances."""
    name = agent_class.__name__
    if name not in _agent_cache:
        _agent_cache[name] = agent_class()
    return _agent_cache[name]


def _build_state_from_context(context: str) -> dict:
    """Build a minimal state dict from a context string for agent prompt formatting."""
    messages = []
    if context:
        messages.append(HumanMessage(content=context))
    return {"messages": messages}


def _create_agent_tool_fn(agent_class, tool_name: str):
    """Create a tool function that delegates to an actual agent instance."""

    @track(name=tool_name)
    def agent_tool_fn(message: str, context: str = "") -> str:
        agent = _get_agent(agent_class)
        state = _build_state_from_context(context)
        prompt = agent.get_prompt(state)
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=message),
        ]
        response = agent.model.invoke(messages)
        return response.content

    return agent_tool_fn


def _build_tools():
    """Build all agent tools. Imports are deferred to avoid circular imports."""
    from app.agents.negative_agent.negative_agent import NegativeAgent
    from app.agents.neutral_agent.neutral_agent import NeutralAgent
    from app.agents.positive_agent.positive_agent import PositiveAgent
    from app.agents.problem_solver_agent.problem_solver_agent import ProblemSolverAgent

    positive = StructuredTool.from_function(
        func=_create_agent_tool_fn(PositiveAgent, "positive_agent_tool"),
        name="positive_therapy",
        description="Use when user feels POSITIVE (happy, good, excited, grateful). Provides celebratory, validating support.",
        args_schema=TherapyInput,
    )

    neutral = StructuredTool.from_function(
        func=_create_agent_tool_fn(NeutralAgent, "neutral_agent_tool"),
        name="neutral_therapy",
        description="Use when user feels NEUTRAL (okay, fine, so-so). Provides balanced exploration and check-in.",
        args_schema=TherapyInput,
    )

    negative = StructuredTool.from_function(
        func=_create_agent_tool_fn(NegativeAgent, "negative_agent_tool"),
        name="negative_therapy",
        description="Use when user feels NEGATIVE (sad, anxious, stressed, overwhelmed). Provides compassionate support.",
        args_schema=TherapyInput,
    )

    problem_solver = StructuredTool.from_function(
        func=_create_agent_tool_fn(ProblemSolverAgent, "problem_solver_agent_tool"),
        name="problem_solver",
        description="Use when user wants SOLUTIONS or practical advice for their challenges.",
        args_schema=TherapyInput,
    )

    return positive, neutral, negative, problem_solver


def get_agent_tools():
    """Get all agent-backed tools for the orchestrator."""
    return list(_build_tools())

