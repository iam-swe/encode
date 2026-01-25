"""
Agent registry using Pydantic for type-safe agent definitions.
Single source of truth for all agent metadata.
Uses Gemini 2.5 Flash as the sole LLM provider.
"""

from typing import Any, Type

from pydantic import BaseModel, ConfigDict, Field

from app.agents.agent_types import (
    GUARDRAILS_AGENT_NAME,
    NEGATIVE_AGENT_NAME,
    NEUTRAL_AGENT_NAME,
    ORCHESTRATOR_NAME,
    POSITIVE_AGENT_NAME,
    PROBLEM_SOLVER_NAME,
    SYNTHESIZER_AGENT_NAME,
)
from app.agents.llm_models import LLMModels


class AgentDefinition(BaseModel):
    """Definition for an agent with its configuration."""

    name: str = Field(description="Canonical agent name")
    display_name: str = Field(description="Human-readable name")
    agent_class: Type[Any] = Field(description="Actual Python class")
    default_model: str = Field(default=LLMModels.GEMINI_2_5_FLASH, description="Default LLM model")
    default_temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    is_workflow: bool = Field(default=False, description="True for composite workflows")

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)


class AgentRegistry:
    """Registry of all available agents using Gemini 2.5 Flash."""

    @classmethod
    def get_orchestrator(cls) -> AgentDefinition:
        from app.agents.orchestrator_agent.orchestrator_agent import OrchestratorAgent

        return AgentDefinition(
            name=ORCHESTRATOR_NAME,
            display_name="Orchestrator Agent",
            agent_class=OrchestratorAgent,
            default_model=LLMModels.GEMINI_2_5_FLASH,
            default_temperature=0.7,
        )

    @classmethod
    def get_positive_agent(cls) -> AgentDefinition:
        from app.agents.positive_agent.positive_agent import PositiveAgent

        return AgentDefinition(
            name=POSITIVE_AGENT_NAME,
            display_name="Positive Mood Agent",
            agent_class=PositiveAgent,
            default_model=LLMModels.GEMINI_2_5_FLASH,
            default_temperature=0.7,
        )

    @classmethod
    def get_neutral_agent(cls) -> AgentDefinition:
        from app.agents.neutral_agent.neutral_agent import NeutralAgent

        return AgentDefinition(
            name=NEUTRAL_AGENT_NAME,
            display_name="Neutral Mood Agent",
            agent_class=NeutralAgent,
            default_model=LLMModels.GEMINI_2_5_FLASH,
            default_temperature=0.7,
        )

    @classmethod
    def get_negative_agent(cls) -> AgentDefinition:
        from app.agents.negative_agent.negative_agent import NegativeAgent

        return AgentDefinition(
            name=NEGATIVE_AGENT_NAME,
            display_name="Negative Mood Agent",
            agent_class=NegativeAgent,
            default_model=LLMModels.GEMINI_2_5_FLASH,
            default_temperature=0.7,
        )

    @classmethod
    def get_problem_solver(cls) -> AgentDefinition:
        from app.agents.problem_solver_agent.problem_solver_agent import ProblemSolverAgent

        return AgentDefinition(
            name=PROBLEM_SOLVER_NAME,
            display_name="Problem Solver Agent",
            agent_class=ProblemSolverAgent,
            default_model=LLMModels.GEMINI_2_5_FLASH,
            default_temperature=0.7,
        )

    @classmethod
    def get_guardrails_agent(cls) -> AgentDefinition:
        from app.agents.guardrails_agent.guardrails_agent import GuardrailsAgent

        return AgentDefinition(
            name=GUARDRAILS_AGENT_NAME,
            display_name="Guardrails Agent",
            agent_class=GuardrailsAgent,
            default_model=LLMModels.GEMINI_2_5_FLASH,
            default_temperature=0.1,
        )

    @classmethod
    def get_synthesizer_agent(cls) -> AgentDefinition:
        from app.agents.synthesizer_agent.synthesizer_agent import SynthesizerAgent

        return AgentDefinition(
            name=SYNTHESIZER_AGENT_NAME,
            display_name="Synthesizer Agent",
            agent_class=SynthesizerAgent,
            default_model=LLMModels.GEMINI_2_5_FLASH,
            default_temperature=0.5,
        )

    @classmethod
    def get_all_agents(cls) -> list[AgentDefinition]:
        return [
            cls.get_orchestrator(),
            cls.get_positive_agent(),
            cls.get_neutral_agent(),
            cls.get_negative_agent(),
            cls.get_problem_solver(),
            cls.get_guardrails_agent(),
            cls.get_synthesizer_agent(),
        ]
