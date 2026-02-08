"""
Problem Solver Agent for the Therapy System.

Provides solution-focused support for users seeking practical paths forward.
"""

from typing import Any, Dict, Optional

import structlog
from pydantic import BaseModel, Field

from app.agents.agent_types import PROBLEM_SOLVER_NAME
from app.agents.base_agent import BaseAgent
from app.agents.llm_models import LLMModels
from app.agents.state import TherapyState

logger = structlog.get_logger(__name__)


class ProblemSolverResponse(BaseModel):
    """Response format for problem solver agent."""

    response: str = Field(description="The solution-focused response")
    actionable_steps: bool = Field(description="Whether actionable steps were provided")


PROBLEM_SOLVER_PROMPT = """You are a solution-focused therapeutic companion helping users find practical paths forward.

YOUR ROLE:
- Help identify specific, actionable steps
- Break down overwhelming problems
- Explore options collaboratively
- Support decision-making without being directive
- Encourage achievable first steps

STYLE:
- Collaborative and empowering
- Focus on what's within their control
- Practical yet emotionally attuned
- Celebrate small wins

CONVERSATION CONTEXT:
{context}

Remember: Guide them to their own solutions. Keep responses under 150 words. End with a clarifying question or suggested next step."""


class ProblemSolverAgent(BaseAgent):
    """Agent for providing solution-focused therapeutic support."""

    def __init__(
        self,
        agent_name: str = PROBLEM_SOLVER_NAME,
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

    def get_result_key(self) -> str:
        return "problem_solver_result"

    def get_prompt(self, state: Optional[TherapyState] = None) -> str:
        from app.agents.state import get_conversation_context

        context = get_conversation_context(state) if state else ""
        return PROBLEM_SOLVER_PROMPT.format(context=context)

    def get_response_format(self) -> type[BaseModel]:
        return ProblemSolverResponse

    async def process_query(
        self,
        query: str,
        state: Optional[TherapyState] = None,
    ) -> Dict[str, Any]:
        """Process a query with solution-focused support."""
        try:
            from langchain_core.messages import HumanMessage, SystemMessage

            prompt = self.get_prompt(state)
            messages = [
                SystemMessage(content=prompt),
                HumanMessage(content=query),
            ]
            response = await self.model.ainvoke(messages)

            return {
                "success": True,
                self.get_result_key(): response.content,
                "error": [],
            }
        except Exception as e:
            logger.error("Problem solver processing failed", error=str(e))
            return {
                "success": False,
                self.get_result_key(): None,
                "error": [str(e)],
            }
