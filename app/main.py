"""
Main entry point for the Encode Therapy System.
"""

import structlog
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.agents.agent_factory import create_multi_agent_workflow
from app.workflows.multi_agentic_workflow import MultiAgentWorkflow

logger = structlog.get_logger(__name__)


def create_app(conversation_id: str | None = None) -> MultiAgentWorkflow:
    """Create and configure the multi-agent workflow application.
    
    Args:
        conversation_id: Optional conversation ID to resume an existing conversation
    """
    logger.info("Initializing Encode Therapy System")
    workflow = create_multi_agent_workflow(conversation_id)
    logger.info("Encode Therapy System initialized successfully")
    return workflow


def run(query: str, conversation_id: str | None = None) -> str:
    """Run a single query through the therapy workflow.

    Args:
        query: The user's message/query
        conversation_id: Optional conversation ID to resume an existing conversation

    Returns:
        The therapist's response
    """
    workflow = create_app(conversation_id)
    response = workflow.chat(query)
    return response


def start_session(conversation_id: str | None = None) -> None:
    """Start a therapy session with an initial greeting, then process one user message."""
    workflow = create_app(conversation_id)

    # Get initial greeting from orchestrator
    initial_response = workflow.chat("Hello")
    print(f"\nTherapist: {initial_response}\n")

    # Wait for user input
    user_input = input("You: ").strip()
    if user_input:
        response = workflow.chat(user_input)
        print(f"\nTherapist: {response}\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Get query from command line arguments
        query = " ".join(sys.argv[1:])
        response = run(query)
        print(f"\nTherapist: {response}\n")
    else:
        # Start a session with greeting first
        start_session()

