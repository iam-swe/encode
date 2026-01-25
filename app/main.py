"""
Main entry point for the Encode Therapy System.
"""

import structlog

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


def run_interactive_session() -> None:
    """Run an interactive therapy session in the terminal."""

    print("\n" + "=" * 60)
    print("       Encode Therapeutic Support System")
    print("=" * 60)
    print("\nWelcome. I'm here to provide a supportive space for you.")
    print("\nCommands:")
    print("  'quit' or 'exit' - End the session")
    print("  'reset' - Start a new conversation")
    print("  'history' - List all saved conversations")
    print("  'load <id>' - Load a previous conversation")
    print("  'delete' - Delete current conversation\n")

    workflow = create_app()
    print(f"[Session ID: {workflow.conversation_id}]\n")

    initial_response = workflow.chat("Hello")
    print(f"\nTherapist: {initial_response}\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "bye"]:
                print("\nTherapist: Thank you for sharing with me today.")
                print("Remember, reaching out takes courage. Take care of yourself.")
                print(f"\n[Conversation saved as: {workflow.conversation_id}]\n")
                break

            if user_input.lower() == "reset":
                workflow.reset()
                print(f"\n[New session started: {workflow.conversation_id}]\n")
                response = workflow.chat("Hello")
                print(f"\nTherapist: {response}\n")
                continue

            if user_input.lower() == "history":
                conversations = workflow.list_conversations()
                if conversations:
                    print("\n[Saved Conversations:]")
                    for conv in conversations[:10]:  # Show last 10
                        print(f"  - {conv['conversation_id']} ({conv['message_count']} messages, {conv['updated_at'][:10]})")
                    print()
                else:
                    print("\n[No saved conversations found]\n")
                continue

            if user_input.lower().startswith("load "):
                conv_id = user_input[5:].strip()
                if workflow.load_conversation(conv_id):
                    print(f"\n[Loaded conversation: {conv_id}]")
                    print("[Continuing previous conversation...]\n")
                else:
                    print(f"\n[Conversation '{conv_id}' not found]\n")
                continue

            if user_input.lower() == "delete":
                if workflow.delete_conversation():
                    print(f"\n[Deleted conversation: {workflow.conversation_id}]")
                    workflow.reset()
                    print(f"[Started new session: {workflow.conversation_id}]\n")
                else:
                    print("\n[No conversation to delete]\n")
                continue

            response = workflow.chat(user_input)
            print(f"\nTherapist: {response}\n")

        except KeyboardInterrupt:
            print(f"\n\nSession ended. Conversation saved as: {workflow.conversation_id}")
            print("Take care!")
            break
        except Exception as e:
            logger.error("Error during conversation", error=str(e))
            print("\n[Error occurred. Let's continue. How are you feeling?]\n")


if __name__ == "__main__":
    run_interactive_session()
