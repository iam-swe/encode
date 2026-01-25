"""
Core data models for the therapy system.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TherapyMessage(BaseModel):
    """A single message in the therapy conversation."""

    message_id: str = Field(description="Unique identifier for the message")
    text: str = Field(description="The message content")
    role: str = Field(description="Role: 'user' or 'therapist'")
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """Request model for chat interactions."""

    conversation_id: str = Field(description="Unique conversation identifier")
    message: TherapyMessage = Field(description="The user's message")
    conversation_history: Optional[List[TherapyMessage]] = Field(
        default=None, description="Previous messages in the conversation"
    )
    user_mood: Optional[str] = Field(default=None, description="Detected user mood")
    user_intent: Optional[str] = Field(default=None, description="Detected user intent")

    def get_conversation_history_as_string(self) -> str:
        """Get conversation history as a formatted string."""
        if not self.conversation_history:
            return ""

        lines = []
        for msg in self.conversation_history:
            role = "User" if msg.role == "user" else "Therapist"
            lines.append(f"{role}: {msg.text}")

        return "\n".join(lines)


class ChatResponse(BaseModel):
    """Response model for chat interactions."""

    conversation_id: str = Field(description="Unique conversation identifier")
    message: TherapyMessage = Field(description="The therapist's response")
    user_mood: Optional[str] = Field(default=None, description="Detected user mood")
    user_intent: Optional[str] = Field(default=None, description="Detected user intent")
    success: bool = Field(default=True, description="Whether the request was successful")
    error: Optional[str] = Field(default=None, description="Error message if any")
