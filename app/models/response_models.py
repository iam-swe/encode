"""
Response models for agent outputs.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class TherapyResponse(BaseModel):
    """Standard response format for therapy agents."""

    response: str = Field(description="The therapeutic response")
    mood_acknowledged: bool = Field(default=True, description="Whether the mood was acknowledged")


class OrchestratorResponse(BaseModel):
    """Response format for the orchestrator agent."""

    selected_agent: str = Field(description="The agent selected to handle this query")
    reasoning: str = Field(description="Why this agent was selected")
    context_summary: str = Field(description="Summary of conversation context")
    response: Optional[str] = Field(default=None, description="The final response")


class GuardrailsResponse(BaseModel):
    """Response format for guardrails checks."""

    approved: bool = Field(description="Whether the response passed safety checks")
    modified_response: Optional[str] = Field(
        default=None, description="Modified response if changes were needed"
    )
    reason: Optional[str] = Field(
        default=None, description="Reason for modification or blocking"
    )
    blocked: bool = Field(default=False, description="Whether the response was blocked")


class SynthesizerResponse(BaseModel):
    """Response format for the synthesizer agent."""

    polished_response: str = Field(description="The polished, synthesized response")
    changes_made: bool = Field(default=True, description="Whether changes were made to the original")


class ProblemSolverResponse(BaseModel):
    """Response format for the problem solver agent."""

    response: str = Field(description="The solution-focused response")
    actionable_steps: List[str] = Field(
        default_factory=list, description="List of suggested actionable steps"
    )
    follow_up_question: Optional[str] = Field(
        default=None, description="Follow-up question to continue the conversation"
    )
