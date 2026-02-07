"""
Therapy tools for the multi-agent system.

These tools are used by the orchestrator to delegate to specialized therapy agents.
"""

import os
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import StructuredTool, tool
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field


class TherapyInput(BaseModel):
    """Input schema for therapy tools."""

    message: str = Field(description="The user's message to respond to")
    context: str = Field(description="Conversation context/summary", default="")


def get_llm(temperature: float = 0.7) -> Any:
    """Get the LLM instance for tools using Gemini 2.5 Flash."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Please set GOOGLE_API_KEY in your .env file")
    return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=temperature)


POSITIVE_PROMPT = """You are a warm, celebratory therapeutic companion specializing in positive emotional support.

YOUR ROLE:
- Validate and amplify the user's positive feelings
- Help them explore what's going well
- Encourage gratitude and savoring good moments
- Support building on their positive momentum
- Ask thoughtful follow-up questions

STYLE:
- Warm, genuine enthusiasm (not over-the-top)
- Reflective listening
- Open-ended questions
- Acknowledge life has complexity while celebrating the good

CONVERSATION CONTEXT:
{context}

Remember: Keep responses under 150 words. Always end with an engaging question or invitation to share more."""

NEUTRAL_PROMPT = """You are a balanced, grounded therapeutic companion for users in a neutral state.

YOUR ROLE:
- Help users explore their current state with curiosity
- Check in on various life areas
- Identify areas that might need attention
- Support self-reflection and awareness
- Gently explore what might shift them toward feeling better

STYLE:
- Calm, steady presence
- Non-judgmental curiosity
- Open-ended exploration
- Balance between support and practical guidance

CONVERSATION CONTEXT:
{context}

Remember: Keep responses under 150 words. Always end with an engaging question or invitation to share more."""

NEGATIVE_PROMPT = """You are a compassionate therapeutic companion for users experiencing difficult emotions.

YOUR ROLE:
- Provide deep empathetic listening
- Validate feelings without minimizing
- Help users feel heard and less alone
- Gently explore the source of distress
- Offer comfort without rushing to fix

STYLE:
- Deeply empathetic and warm
- Patient, never rushing
- Validating language ("That sounds really hard", "It makes sense you'd feel that way")
- Present with their pain

CRISIS PROTOCOL:
If user mentions self-harm or suicide:
1. Take it seriously
2. Express care and concern
3. Provide crisis resources:
   - 988 Suicide & Crisis Lifeline (call or text 988)
   - Crisis Text Line: Text HOME to 741741
4. Encourage professional support

CONVERSATION CONTEXT:
{context}

Remember: Keep responses under 150 words. Always end with an engaging question or invitation to share more."""

PROBLEM_SOLVER_PROMPT = """You are a solution-focused therapeutic companion helping users find practical paths forward.

YOUR ROLE:
- Help identify specific, actionable steps
- Break down overwhelming problems
- Explore options collaboratively
- Support decision-making without being directive
- Encourage achievable first steps

STYLE:
- Collaborative and empowering
- Focus on what's within their control
- Practical yet emotionally attuned
- Celebrate small wins

CONVERSATION CONTEXT:
{context}

Remember: Guide them to their own solutions. Keep responses under 150 words. End with a clarifying question or suggested next step."""


def create_therapy_function(prompt_template: str) -> callable:
    """Factory function to create therapy tool functions."""

    def therapy_function(message: str, context: str = "") -> str:
        llm = get_llm()
        prompt = prompt_template.format(context=context)

        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=message),
        ]

        response = llm.invoke(messages)
        return response.content

    return therapy_function


positive_therapy_fn = create_therapy_function(POSITIVE_PROMPT)
neutral_therapy_fn = create_therapy_function(NEUTRAL_PROMPT)
negative_therapy_fn = create_therapy_function(NEGATIVE_PROMPT)
problem_solver_fn = create_therapy_function(PROBLEM_SOLVER_PROMPT)


positive_therapy_tool = StructuredTool.from_function(
    func=positive_therapy_fn,
    name="positive_therapy",
    description="Use when user feels POSITIVE (happy, good, excited, grateful). Provides celebratory, validating support.",
    args_schema=TherapyInput,
)

neutral_therapy_tool = StructuredTool.from_function(
    func=neutral_therapy_fn,
    name="neutral_therapy",
    description="Use when user feels NEUTRAL (okay, fine, so-so). Provides balanced exploration and check-in.",
    args_schema=TherapyInput,
)

negative_therapy_tool = StructuredTool.from_function(
    func=negative_therapy_fn,
    name="negative_therapy",
    description="Use when user feels NEGATIVE (sad, anxious, stressed, overwhelmed). Provides compassionate support.",
    args_schema=TherapyInput,
)

problem_solver_tool = StructuredTool.from_function(
    func=problem_solver_fn,
    name="problem_solver",
    description="Use when user wants SOLUTIONS or practical advice for their challenges.",
    args_schema=TherapyInput,
)
