"""
Negative Mood Agent for the Therapy System.

Provides compassionate support for users experiencing difficult emotions.
"""

from typing import Any, Dict, Optional

import structlog
from pydantic import BaseModel, Field

from app.agents.agent_types import NEGATIVE_AGENT_NAME
from app.agents.base_agent import BaseAgent
from app.agents.llm_models import LLMModels
from app.agents.state import TherapyState
from app.constants import CRISIS_RESOURCES

logger = structlog.get_logger(__name__)


class TherapyResponse(BaseModel):
    """Response format for therapy agents."""

    response: str = Field(description="The therapeutic response")
    mood_acknowledged: bool = Field(description="Whether the mood was acknowledged")
    crisis_detected: bool = Field(default=False, description="Whether crisis indicators were detected")


NEGATIVE_AGENT_PROMPT = """You are a compassionate therapeutic companion for users experiencing difficult emotions.

YOUR ROLE:
- Provide deep empathetic listening
- Validate feelings without minimizing
- Help users feel heard and less alone
- Gently explore the source of distress
- Offer comfort without rushing to fix

STYLE:
- Deeply empathetic and warm
- Patient, never rushing
- Validating language ("That sounds really hard", "It makes sense you'd feel that way")
- Present with their pain

CRISIS PROTOCOL:
If user mentions self-harm or suicide:
1. Take it seriously
2. Express care and concern
3. Provide crisis resources:
   - {suicide_lifeline}
   - {crisis_text}
4. Encourage professional support

CONVERSATION CONTEXT:
{{context}}

Remember: Keep responses under 150 words. Always end with an engaging question or invitation to share more."""


class NegativeAgent(BaseAgent):
    """Agent for handling negative mood therapeutic conversations."""

    def __init__(
        self,
        agent_name: str = NEGATIVE_AGENT_NAME,
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
        return "negative_agent_result"

    def get_prompt(self, state: Optional[TherapyState] = None) -> str:
        from app.agents.state import get_conversation_context

        context = get_conversation_context(state) if state else ""
        prompt = NEGATIVE_AGENT_PROMPT.format(
            suicide_lifeline=CRISIS_RESOURCES["suicide_lifeline"],
            crisis_text=CRISIS_RESOURCES["crisis_text"],
        )
        return prompt.format(context=context)

    def get_response_format(self) -> type[BaseModel]:
        return TherapyResponse

    async def process_query(
        self,
        query: str,
        state: Optional[TherapyState] = None,
    ) -> Dict[str, Any]:
        """Process a query with compassionate negative mood support."""
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
            logger.error("Negative agent processing failed", error=str(e))
            return {
                "success": False,
                self.get_result_key(): None,
                "error": [str(e)],
            }
