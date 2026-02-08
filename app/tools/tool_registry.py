"""
Tool registry for managing available tools.
"""

from typing import Any, Dict, List

from langchain_core.tools import BaseTool

TOOL_REGISTRY: Dict[str, Any] = {}


def register_tool(name: str, tool_callable: Any) -> None:
    """Register a tool in the registry."""
    TOOL_REGISTRY[name] = tool_callable


def get_tool(name: str) -> Any:
    """Get a tool from the registry by name."""
    return TOOL_REGISTRY.get(name)


def get_all_tools() -> List[BaseTool]:
    """Get all registered agent tools."""
    from app.tools.therapy_tools import get_agent_tools

    return get_agent_tools()


def initialize_tools() -> None:
    """Initialize and register all agent tools."""
    from app.agents.agent_types import (
        NEGATIVE_AGENT_NAME,
        NEUTRAL_AGENT_NAME,
        POSITIVE_AGENT_NAME,
        PROBLEM_SOLVER_NAME,
    )

    from app.tools.therapy_tools import get_agent_tools

    tools = get_agent_tools()
    names = [POSITIVE_AGENT_NAME, NEUTRAL_AGENT_NAME, NEGATIVE_AGENT_NAME, PROBLEM_SOLVER_NAME]
    for name, tool in zip(names, tools):
        register_tool(name, tool)