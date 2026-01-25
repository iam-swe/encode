"""
Orchestrator Agent for the Therapy System.

Routes conversations to appropriate therapy agents based on mood and intent.
"""

from typing import Any, Dict, List, Optional

import structlog
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from app.agents.agent_types import ORCHESTRATOR_NAME
from app.agents.base_agent import BaseAgent
from app.agents.llm_models import LLMModels
from app.agents.state import TherapyState
from app.tools.tool_registry import get_tool

logger = structlog.get_logger(__name__)


class OrchestratorResponse(BaseModel):
    """Response format for the orchestrator agent."""

    selected_agent: str = Field(description="The agent selected to handle this query")
    reasoning: str = Field(description="Why this agent was selected")
    context_summary: str = Field(description="Summary of conversation context")


ORCHESTRATOR_PROMPT = """You are the orchestrator of a therapeutic support system.

YOUR PRIMARY RESPONSIBILITIES:
1. GREET users warmly on first interaction
2. ASSESS their emotional state (positive, neutral, or negative)
3. DETERMINE their intent (want to talk vs. want solutions)
4. ROUTE to appropriate therapy agent using tools
5. MAINTAIN conversation continuity

CONVERSATION FLOW:
1. First message: Greet warmly, ask how they're feeling
2. After mood shared: Acknowledge and ask "Would you like to talk about your feelings, or are you looking for some solutions/advice?"
3. Based on response: Use appropriate tool

TOOL SELECTION GUIDE:
- POSITIVE mood (happy, excited, grateful, good) → positive_therapy
- NEUTRAL mood (okay, fine, so-so, alright) → neutral_therapy
- NEGATIVE mood (sad, anxious, stressed, overwhelmed, frustrated) → negative_therapy
- Wants SOLUTIONS/ADVICE → problem_solver

CURRENT STATE:
- Mood: {mood}
- Intent: {intent}
- Phase: {phase}

IMPORTANT:
- Be brief in your own responses - let therapy tools do the work
- Always use a tool when the user shares something substantive
- Build conversation context from the history
- If mood/intent unclear, ask clarifying questions first

CRISIS RESOURCES (share when needed):
- 988 Suicide & Crisis Lifeline
- Crisis Text Line: Text HOME to 741741
"""


class OrchestratorAgent(BaseAgent):
    """Orchestrator agent for routing therapy conversations."""

    def __init__(
        self,
        agent_name: str = ORCHESTRATOR_NAME,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        model_name: str = LLMModels.GEMINI_2_5_FLASH,
    ) -> None:
        super().__init__(
            agent_name=agent_name,
            api_key=api_key,
            temperature=temperature,
            model_name=model_name,
        )

    def get_tools(self) -> List[BaseTool]:
        """Get therapy tools for the orchestrator."""
        from app.agents.agent_types import (
            NEGATIVE_AGENT_NAME,
            NEUTRAL_AGENT_NAME,
            POSITIVE_AGENT_NAME,
            PROBLEM_SOLVER_NAME,
        )

        tools = []
        for tool_name in [POSITIVE_AGENT_NAME, NEUTRAL_AGENT_NAME, NEGATIVE_AGENT_NAME, PROBLEM_SOLVER_NAME]:
            tool = get_tool(tool_name)
            if tool:
                tools.append(tool)
        return tools

    def get_result_key(self) -> str:
        return "orchestrator_result"

    def get_prompt(self, state: Optional[TherapyState] = None) -> str:
        mood = state.get("user_mood", "unknown") if state else "unknown"
        intent = state.get("user_intent", "unknown") if state else "unknown"
        phase = state.get("phase", "greeting") if state else "greeting"

        return ORCHESTRATOR_PROMPT.format(mood=mood, intent=intent, phase=phase)

    def get_response_format(self) -> type[BaseModel]:
        return OrchestratorResponse

    async def process_query(
        self,
        query: str,
        state: Optional[TherapyState] = None,
    ) -> Dict[str, Any]:
        """Process a query through the orchestrator."""
        try:
            from langgraph.prebuilt import create_react_agent

            tools = self.get_tools()
            prompt = self.get_prompt(state)

            agent = create_react_agent(self.model, tools, state_modifier=prompt)

            result = agent.invoke({"messages": state.get("messages", []) if state else []})

            return {
                "success": True,
                "orchestrator_result": result,
                "messages": result.get("messages", []),
                "error": [],
            }
        except Exception as e:
            logger.error("Orchestrator processing failed", error=str(e))
            return {
                "success": False,
                "orchestrator_result": None,
                "error": [str(e)],
            }
