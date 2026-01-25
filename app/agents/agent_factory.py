"""
Agent factory for creating and managing agent singletons.
"""

from typing import Any, Dict, cast

import structlog

from app.agents import (
    GuardrailsAgent,
    NegativeAgent,
    NeutralAgent,
    OrchestratorAgent,
    PositiveAgent,
    ProblemSolverAgent,
    SynthesizerAgent,
)
from app.agents.agent_types import (
    GUARDRAILS_AGENT_NAME,
    NEGATIVE_AGENT_NAME,
    NEUTRAL_AGENT_NAME,
    ORCHESTRATOR_NAME,
    POSITIVE_AGENT_NAME,
    PROBLEM_SOLVER_NAME,
    SYNTHESIZER_AGENT_NAME,
)
from app.agents.config import AgentConfig, AgentFactoryConfig

logger = structlog.get_logger(__name__)

_singletons: Dict[str, Any] = {}
_initialized: bool = False


def _create_agent_with_config(agent_name: str, agent_class: type, config: AgentConfig) -> Any:
    """Create an agent instance with the given configuration."""
    return agent_class(
        model_name=config.model_name,
        temperature=config.temperature,
        provider=config.provider,
    )


def initialize_agents(config: AgentFactoryConfig | None = None) -> None:
    """Initialize all agent singletons."""
    global _singletons, _initialized

    if _initialized:
        logger.info("Agents already initialized")
        return

    if config is None:
        config = AgentFactoryConfig()

    logger.info("Initializing agents")

    # Create all agents
    _singletons[ORCHESTRATOR_NAME] = _create_agent_with_config(
        ORCHESTRATOR_NAME,
        OrchestratorAgent,
        config.orchestrator_agent,
    )
    _singletons[POSITIVE_AGENT_NAME] = _create_agent_with_config(
        POSITIVE_AGENT_NAME,
        PositiveAgent,
        config.positive_agent,
    )
    _singletons[NEUTRAL_AGENT_NAME] = _create_agent_with_config(
        NEUTRAL_AGENT_NAME,
        NeutralAgent,
        config.neutral_agent,
    )
    _singletons[NEGATIVE_AGENT_NAME] = _create_agent_with_config(
        NEGATIVE_AGENT_NAME,
        NegativeAgent,
        config.negative_agent,
    )
    _singletons[PROBLEM_SOLVER_NAME] = _create_agent_with_config(
        PROBLEM_SOLVER_NAME,
        ProblemSolverAgent,
        config.problem_solver_agent,
    )
    _singletons[GUARDRAILS_AGENT_NAME] = _create_agent_with_config(
        GUARDRAILS_AGENT_NAME,
        GuardrailsAgent,
        config.guardrails_agent,
    )
    _singletons[SYNTHESIZER_AGENT_NAME] = _create_agent_with_config(
        SYNTHESIZER_AGENT_NAME,
        SynthesizerAgent,
        config.synthesizer_agent,
    )

    _initialized = True
    logger.info("All agents initialized successfully")


def get_agent(agent_name: str) -> Any:
    """Get an agent singleton by name."""
    if not _initialized:
        initialize_agents()
    return _singletons.get(agent_name)


def create_multi_agent_workflow(conversation_id: str | None = None) -> "MultiAgentWorkflow":
    """Create and return the multi-agent workflow.
    
    Args:
        conversation_id: Optional conversation ID to resume an existing conversation
    """
    from app.nodes.guardrails_node import GuardrailsNode
    from app.nodes.orchestrator_node import OrchestratorNode
    from app.nodes.synthesizer_node import SynthesizerNode
    from app.workflows.multi_agentic_workflow import MultiAgentWorkflow

    if not _initialized:
        initialize_agents()

    orchestrator_agent = cast(OrchestratorAgent, _singletons.get(ORCHESTRATOR_NAME))
    guardrails_agent = cast(GuardrailsAgent, _singletons.get(GUARDRAILS_AGENT_NAME))
    synthesizer_agent = cast(SynthesizerAgent, _singletons.get(SYNTHESIZER_AGENT_NAME))

    orchestrator_node = OrchestratorNode(orchestrator_agent)
    guardrails_node = GuardrailsNode(guardrails_agent)
    synthesizer_node = SynthesizerNode(synthesizer_agent)

    return MultiAgentWorkflow(
        orchestrator_node=orchestrator_node,
        guardrails_node=guardrails_node,
        synthesizer_node=synthesizer_node,
        conversation_id=conversation_id,
    )
