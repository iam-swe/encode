"""
Multi-Agent Workflow for the Therapy System.

Implements a LangGraph workflow that orchestrates multiple therapy agents
in a coordinated manner
"""

import os
from typing import Any, Dict, List, Optional

import structlog
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agents.state import TherapyState, get_initial_state
from app.nodes.guardrails_node import GuardrailsNode
from app.nodes.orchestrator_node import OrchestratorNode
from app.nodes.synthesizer_node import SynthesizerNode
from app.utils.conversation_store import ConversationStore, get_conversation_store

logger = structlog.get_logger(__name__)


class MultiAgentWorkflow:
    """LangGraph workflow with multi-agent integration for therapy conversations.

    Architecture:
        User Message
             |
             v
        Orchestrator (routes to appropriate therapy agent)
             |
             v
        Guardrails (safety check)
             |
             v
        Synthesizer (polish response)
             |
             v
        User Response
    """

    def __init__(
        self,
        orchestrator_node: OrchestratorNode,
        guardrails_node: GuardrailsNode,
        synthesizer_node: SynthesizerNode,
        conversation_id: Optional[str] = None,
    ) -> None:
        self.orchestrator_node = orchestrator_node
        self.guardrails_node = guardrails_node
        self.synthesizer_node = synthesizer_node
        self.conversation_store = get_conversation_store()

        self.memory = MemorySaver()
        self.workflow = self._create_workflow()
        self.conversation_id = conversation_id or f"therapy_session_{hash(str(os.urandom(8)))}"
        self.thread_id = self.conversation_id
        self.config = {"configurable": {"thread_id": self.thread_id}}
        self._state: Optional[TherapyState] = None

        # Load existing conversation if available
        self._load_conversation_history()

        logger.info("MultiAgentWorkflow initialized", conversation_id=self.conversation_id)

    def _create_workflow(self) -> CompiledStateGraph:
        """Create and compile the LangGraph workflow."""

        workflow = StateGraph(TherapyState)

        # Add nodes
        workflow.add_node("orchestrator", self.orchestrator_node.process)
        workflow.add_node("guardrails", self.guardrails_node.process)
        workflow.add_node("synthesizer", self.synthesizer_node.process)

        # Define edges: linear flow through the pipeline
        workflow.add_edge(START, "orchestrator")
        workflow.add_edge("orchestrator", "guardrails")
        workflow.add_edge("guardrails", "synthesizer")
        workflow.add_edge("synthesizer", END)

        return workflow.compile(checkpointer=self.memory)

    def _load_conversation_history(self) -> None:
        """Load conversation history from file storage."""
        stored_messages = self.conversation_store.get_messages(self.conversation_id)
        if stored_messages:
            self._state = get_initial_state()
            messages = []
            for msg in stored_messages:
                if msg.get("role") == "user":
                    messages.append(HumanMessage(content=msg.get("content", "")))
                elif msg.get("role") == "assistant":
                    messages.append(AIMessage(content=msg.get("content", "")))
            self._state["messages"] = messages

            # Load metadata
            conversation_data = self.conversation_store.load_conversation(self.conversation_id)
            if conversation_data and conversation_data.get("metadata"):
                metadata = conversation_data["metadata"]
                self._state["user_mood"] = metadata.get("user_mood", "unknown")
                self._state["user_intent"] = metadata.get("user_intent", "unknown")
                self._state["turn_count"] = metadata.get("turn_count", 0)

            logger.info("Loaded conversation history", conversation_id=self.conversation_id, message_count=len(messages))

    def _save_conversation(self) -> None:
        """Save current conversation to file storage."""
        if self._state is None:
            return

        messages: List[Dict[str, Any]] = []
        for msg in self._state.get("messages", []):
            if isinstance(msg, HumanMessage):
                messages.append({
                    "role": "user",
                    "content": msg.content,
                })
            elif isinstance(msg, AIMessage) and msg.content:
                if not getattr(msg, "tool_calls", None):
                    messages.append({
                        "role": "assistant",
                        "content": msg.content,
                    })

        metadata = {
            "user_mood": self._state.get("user_mood", "unknown"),
            "user_intent": self._state.get("user_intent", "unknown"),
            "turn_count": self._state.get("turn_count", 0),
        }

        self.conversation_store.save_conversation(
            self.conversation_id,
            messages,
            metadata,
        )

    def _get_current_state(self) -> TherapyState:
        """Get the current state or initialize a new one."""
        if self._state is None:
            self._state = get_initial_state()
        return self._state

    async def process_query_async(
        self,
        user_message: str,
    ) -> Dict[str, Any]:
        """Process a query asynchronously through the workflow."""
        try:
            state = self._get_current_state()

            # Add user message
            state["messages"] = list(state.get("messages", [])) + [
                HumanMessage(content=user_message)
            ]
            state["user_query"] = user_message

            # Invoke workflow
            final_state = await self.workflow.ainvoke(state, self.config)

            # Update internal state
            self._state = dict(final_state)

            # Save conversation to file
            self._save_conversation()

            # Extract response
            response = self._extract_response(final_state)

            return {
                "success": True,
                "response": response,
                "state": final_state,
            }

        except Exception as e:
            logger.error("Workflow processing failed", error=str(e))
            return {
                "success": False,
                "response": "I'm here to listen. How are you feeling?",
                "error": str(e),
            }

    def process_query(self, user_message: str) -> Dict[str, Any]:
        """Process a query synchronously through the workflow."""
        try:
            state = self._get_current_state()

            # Add user message
            state["messages"] = list(state.get("messages", [])) + [
                HumanMessage(content=user_message)
            ]
            state["user_query"] = user_message

            # Invoke workflow
            final_state = self.workflow.invoke(state, self.config)

            # Update internal state
            self._state = dict(final_state)

            # Save conversation to file
            self._save_conversation()

            # Extract response
            response = self._extract_response(final_state)

            return {
                "success": True,
                "response": response,
                "state": final_state,
            }

        except Exception as e:
            logger.error("Workflow processing failed", error=str(e))
            return {
                "success": False,
                "response": "I'm here to listen. How are you feeling?",
                "error": str(e),
            }

    def _extract_response(self, state: TherapyState) -> str:
        """Extract the final response from state."""
        # First check current_response
        if state.get("current_response"):
            return state["current_response"]

        # Then check messages for last AI message
        for msg in reversed(state.get("messages", [])):
            if isinstance(msg, AIMessage) and msg.content:
                if not getattr(msg, "tool_calls", None):
                    return msg.content

        return "I'm here to listen. How are you feeling?"

    def chat(self, user_message: str) -> str:
        """Simple chat interface that returns just the response string."""
        result = self.process_query(user_message)
        return result.get("response", "I'm here to listen. How are you feeling?")

    def get_greeting(self) -> str:
        """Get initial greeting from the orchestrator."""
        try:
            model = self.orchestrator_node.orchestrator_agent.model

            # Simple direct call to get greeting - no tools needed
            response = model.invoke(
                "You are a warm, supportive therapy assistant. Generate a brief, welcoming greeting for a new user starting a therapy session. Ask how they're feeling today. Keep it to 1-2 sentences."
            )

            if response and response.content:
                return response.content


            return "Hi there! I'm here to support you. How are you feeling today?"

        except Exception as e:
            logger.error("Failed to get greeting", error=str(e))
            return "Hi there! I'm here to support you. How are you feeling today?"

    def reset(self) -> None:
        """Reset the conversation state and start a new conversation."""
        self._state = None
        self.conversation_id = f"therapy_session_{hash(str(os.urandom(8)))}"
        self.thread_id = self.conversation_id
        self.config = {"configurable": {"thread_id": self.thread_id}}
        logger.info("Workflow state reset", new_conversation_id=self.conversation_id)

    def delete_conversation(self) -> bool:
        """Delete the current conversation from storage."""
        return self.conversation_store.delete_conversation(self.conversation_id)

    def list_conversations(self) -> List[Dict[str, Any]]:
        """List all stored conversations."""
        return self.conversation_store.list_conversations()

    def load_conversation(self, conversation_id: str) -> bool:
        """Load a specific conversation by ID.
        
        Args:
            conversation_id: The ID of the conversation to load
            
        Returns:
            True if conversation was loaded, False if not found
        """
        self.conversation_id = conversation_id
        self.thread_id = conversation_id
        self.config = {"configurable": {"thread_id": self.thread_id}}
        self._state = None
        self._load_conversation_history()
        return self._state is not None

    def get_state(self) -> Optional[TherapyState]:
        """Get the current conversation state."""
        return self._state
