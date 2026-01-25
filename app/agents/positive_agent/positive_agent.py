"""
Positive Mood Agent for the Therapy System.

Provides therapeutic support for users experiencing positive emotions.
"""

from typing import Any, Dict, Optional

import structlog
from pydantic import BaseModel, Field

from app.agents.agent_types import POSITIVE_AGENT_NAME
from app.agents.base_agent import BaseAgent
from app.agents.llm_models import LLMModels
from app.agents.state import TherapyState

logger = structlog.get_logger(__name__)


class TherapyResponse(BaseModel):
    """Response format for therapy agents."""

    response: str = Field(description="The therapeutic response")
    mood_acknowledged: bool = Field(description="Whether the mood was acknowledged")


POSITIVE_AGENT_PROMPT = """You are a warm, celebratory therapeutic companion specializing in positive emotional support.

YOUR ROLE:
- Validate and amplify the user's positive feelings
- Help them explore what's going well
- Encourage gratitude and savoring good moments
- Support building on their positive momentum
- Ask thoughtful follow-up questions

STYLE:
- Warm, genuine enthusiasm (not over-the-top)
- Reflective listening
- Open-ended questions
- Acknowledge life has complexity while celebrating the good

CONVERSATION CONTEXT:
{context}

Remember: Keep responses under 150 words. Always end with an engaging question or invitation to share more."""


class PositiveAgent(BaseAgent):
    """Agent for handling positive mood therapeutic conversations."""

    def __init__(
        self,
        agent_name: str = POSITIVE_AGENT_NAME,
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
        return "positive_agent_result"

    def get_prompt(self, state: Optional[TherapyState] = None) -> str:
        from app.agents.state import get_conversation_context

        context = get_conversation_context(state) if state else ""
        return POSITIVE_AGENT_PROMPT.format(context=context)

    def get_response_format(self) -> type[BaseModel]:
        return TherapyResponse

    async def process_query(
        self,
        query: str,
        state: Optional[TherapyState] = None,
    ) -> Dict[str, Any]:
        """Process a query with positive mood support."""
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
            logger.error("Positive agent processing failed", error=str(e))
            return {
                "success": False,
                self.get_result_key(): None,
                "error": [str(e)],
            }
