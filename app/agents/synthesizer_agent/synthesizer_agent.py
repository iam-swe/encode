"""
Synthesizer Agent for the Therapy System.

Polishes and formats final responses for natural conversation flow.
"""

from typing import Any, Dict, Optional

import structlog
from pydantic import BaseModel, Field

from app.agents.agent_types import SYNTHESIZER_AGENT_NAME
from app.agents.base_agent import BaseAgent
from app.agents.llm_models import LLMModels
from app.agents.state import TherapyState

logger = structlog.get_logger(__name__)


class SynthesizerResponse(BaseModel):
    """Response format for synthesizer agent."""

    polished_response: str = Field(description="The polished, synthesized response")


SYNTHESIZER_PROMPT = """You are the final response formatter for a therapy chatbot.

Your job:
1. Ensure the response flows naturally and conversationally
2. Add appropriate warmth (but don't overdo it)
3. Make sure there's an invitation to continue (question or open statement)
4. Keep it concise but complete
5. Remove any awkward phrasing

Just output the polished response, nothing else. Keep under 200 words."""


class SynthesizerAgent(BaseAgent):
    """Agent for polishing and synthesizing final responses."""

    def __init__(
        self,
        agent_name: str = SYNTHESIZER_AGENT_NAME,
        api_key: Optional[str] = None,
        temperature: float = 0.5,
        model_name: str = LLMModels.GEMINI_2_5_FLASH,
    ) -> None:
        super().__init__(
            agent_name=agent_name,
            api_key=api_key,
            temperature=temperature,
            model_name=model_name,
        )

    def get_result_key(self) -> str:
        return "synthesizer_result"

    def get_prompt(self, state: Optional[TherapyState] = None) -> str:
        return SYNTHESIZER_PROMPT

    def get_response_format(self) -> type[BaseModel]:
        return SynthesizerResponse

    async def synthesize(self, response_to_polish: str) -> Dict[str, Any]:
        """Synthesize and polish a response."""
        try:
            from langchain_core.messages import HumanMessage, SystemMessage

            prompt = self.get_prompt()
            messages = [
                SystemMessage(content=prompt),
                HumanMessage(content=f"Polish this response:\n\n{response_to_polish}"),
            ]

            result = await self.model.ainvoke(messages)

            return {
                "success": True,
                "polished_response": result.content,
                "error": [],
            }
        except Exception as e:
            logger.error("Synthesizer failed", error=str(e))
            return {
                "success": False,
                "polished_response": response_to_polish,
                "error": [str(e)],
            }

    def synthesize_sync(self, response_to_polish: str) -> Dict[str, Any]:
        """Synchronous version of synthesize."""
        try:
            from langchain_core.messages import HumanMessage, SystemMessage

            prompt = self.get_prompt()
            messages = [
                SystemMessage(content=prompt),
                HumanMessage(content=f"Polish this response:\n\n{response_to_polish}"),
            ]

            result = self.model.invoke(messages)

            return {
                "success": True,
                "polished_response": result.content,
                "error": [],
            }
        except Exception as e:
            logger.error("Synthesizer failed", error=str(e))
            return {
                "success": False,
                "polished_response": response_to_polish,
                "error": [str(e)],
            }
