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
    """Get all registered tools."""
    from app.tools.therapy_tools import (
        negative_therapy_tool,
        neutral_therapy_tool,
        positive_therapy_tool,
        problem_solver_tool,
    )

    return [
        positive_therapy_tool,
        neutral_therapy_tool,
        negative_therapy_tool,
        problem_solver_tool,
    ]


def initialize_tools() -> None:
    """Initialize and register all tools."""
    from app.agents.agent_types import (
        NEGATIVE_AGENT_NAME,
        NEUTRAL_AGENT_NAME,
        POSITIVE_AGENT_NAME,
        PROBLEM_SOLVER_NAME,
    )

    from app.tools.therapy_tools import (
        negative_therapy_tool,
        neutral_therapy_tool,
        positive_therapy_tool,
        problem_solver_tool,
    )

    register_tool(POSITIVE_AGENT_NAME, positive_therapy_tool)
    register_tool(NEUTRAL_AGENT_NAME, neutral_therapy_tool)
    register_tool(NEGATIVE_AGENT_NAME, negative_therapy_tool)
    register_tool(PROBLEM_SOLVER_NAME, problem_solver_tool)
