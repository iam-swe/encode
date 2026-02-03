"""
Main entry point for the Encode Therapy System.
"""

import structlog
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.agents.agent_factory import create_multi_agent_workflow
from app.workflows.multi_agentic_workflow import MultiAgentWorkflow
from app.utils.tts import speak
from app.utils.stt import listen

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


def run_interactive_session(conversation_id: str | None = None) -> None:
    """Run an interactive therapy session with continuous conversation."""
    workflow = create_app(conversation_id)

    print("\n" + "=" * 50)
    print("Welcome to Encode Therapy System")
    print("Say 'quit' or 'exit' to end the session")
    print("=" * 50 + "\n")

    # Get initial greeting from orchestrator (empty message triggers greeting)
    initial_response = workflow.get_greeting()
    print(f"Therapist: {initial_response}\n")
    speak(initial_response)

    # Interactive conversation loop
    while True:
        try:
            user_input = listen()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "bye", "goodbye"]:
                goodbye_msg = "Take care of yourself. Remember, it's okay to reach out whenever you need support. Goodbye!"
                print(f"\nTherapist: {goodbye_msg}\n")
                speak(goodbye_msg)
                break

            response = workflow.chat(user_input)
            print(f"\nTherapist: {response}\n")
            speak(response)

        except KeyboardInterrupt:
            print("\n\nTherapist: Take care! Feel free to come back anytime.\n")
            break
        except EOFError:
            print("\n\nSession ended.\n")
            break


def start_session(conversation_id: str | None = None) -> None:
    """Start a therapy session (alias for run_interactive_session)."""
    run_interactive_session(conversation_id)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Get query from command line arguments
        query = " ".join(sys.argv[1:])
        response = run(query)
        print(f"\nTherapist: {response}\n")
        speak(response)
    else:
        # Start a session with greeting first
        start_session()

