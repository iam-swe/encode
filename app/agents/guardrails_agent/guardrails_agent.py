"""
Guardrails Agent for the Therapy System.

Ensures responses are safe, appropriate, and therapeutically sound.
"""

from typing import Any, Dict, Optional

import structlog
from pydantic import BaseModel, Field

from app.agents.agent_types import GUARDRAILS_AGENT_NAME
from app.agents.base_agent import BaseAgent
from app.agents.llm_models import LLMModels
from app.agents.state import TherapyState

logger = structlog.get_logger(__name__)


class GuardrailsResponse(BaseModel):
    """Response format for guardrails agent."""

    approved: bool = Field(description="Whether the response is approved")
    modified_response: Optional[str] = Field(description="Modified response if changes needed")
    reason: Optional[str] = Field(description="Reason for modification or blocking")


GUARDRAILS_PROMPT = """You are a safety filter for a therapy chatbot. Review the response for:

1. HARMFUL content (self-harm encouragement, violence, illegal activities) - BLOCK
2. MEDICAL DIAGNOSES or prescriptions - MODIFY to add disclaimer
3. DISMISSIVE or invalidating language - MODIFY to be more empathetic
4. OVERLY NEGATIVE messaging without hope - MODIFY to add supportive element
5. INAPPROPRIATE crisis response - MODIFY to include resources

Output Format:
- If safe: Return the response as-is
- If needs modification: Return the improved version
- If blocked: Return a safe alternative response

Just output the final response text, nothing else."""


class GuardrailsAgent(BaseAgent):
    """Agent for ensuring response safety and appropriateness."""

    def __init__(
        self,
        agent_name: str = GUARDRAILS_AGENT_NAME,
        api_key: Optional[str] = None,
        temperature: float = 0.1,
        model_name: str = LLMModels.GEMINI_2_5_FLASH,
    ) -> None:
        super().__init__(
            agent_name=agent_name,
            api_key=api_key,
            temperature=temperature,
            model_name=model_name,
        )

    def get_result_key(self) -> str:
        return "guardrails_result"

    def get_prompt(self, state: Optional[TherapyState] = None) -> str:
        return GUARDRAILS_PROMPT

    def get_response_format(self) -> type[BaseModel]:
        return GuardrailsResponse

    async def check_response(self, response_to_check: str) -> Dict[str, Any]:
        """Check a response for safety and appropriateness."""
        try:
            from langchain_core.messages import HumanMessage, SystemMessage

            prompt = self.get_prompt()
            messages = [
                SystemMessage(content=prompt),
                HumanMessage(content=f"Response to review:\n\n{response_to_check}"),
            ]

            result = await self.model.ainvoke(messages)

            return {
                "success": True,
                "checked_response": result.content,
                "guardrail_approved": True,
                "error": [],
            }
        except Exception as e:
            logger.error("Guardrails check failed", error=str(e))
            return {
                "success": False,
                "checked_response": response_to_check,
                "guardrail_approved": False,
                "error": [str(e)],
            }

    def check_response_sync(self, response_to_check: str) -> Dict[str, Any]:
        """Synchronous version of check_response."""
        try:
            from langchain_core.messages import HumanMessage, SystemMessage

            prompt = self.get_prompt()
            messages = [
                SystemMessage(content=prompt),
                HumanMessage(content=f"Response to review:\n\n{response_to_check}"),
            ]

            result = self.model.invoke(messages)

            return {
                "success": True,
                "checked_response": result.content,
                "guardrail_approved": True,
                "error": [],
            }
        except Exception as e:
            logger.error("Guardrails check failed", error=str(e))
            return {
                "success": False,
                "checked_response": response_to_check,
                "guardrail_approved": False,
                "error": [str(e)],
            }
