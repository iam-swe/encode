# Encode - Multi-Agent Therapy System

A multi-agent therapeutic support platform using LangGraph

## Architecture

```
encode/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Application entry point
│   ├── constants.py               # System constants
│   │
│   ├── agents/                    # All agent implementations
│   │   ├── __init__.py
│   │   ├── base_agent.py          # Base agent class
│   │   ├── state.py               # Shared state definition
│   │   ├── registry.py            # Agent registry
│   │   ├── agent_factory.py       # Factory for creating agents
│   │   ├── config.py              # Agent configuration
│   │   ├── agent_types.py         # Agent type constants
│   │   ├── llm_models.py          # LLM model definitions
│   │   │
│   │   ├── orchestrator_agent/    # Routes to appropriate therapy agent
│   │   ├── positive_agent/        # Handles positive mood support
│   │   ├── neutral_agent/         # Handles neutral mood support
│   │   ├── negative_agent/        # Handles negative mood support
│   │   ├── problem_solver_agent/  # Provides solution-focused support
│   │   ├── guardrails_agent/      # Ensures response safety
│   │   └── synthesizer_agent/     # Polishes final responses
│   │
│   ├── nodes/                     # LangGraph node implementations
│   │   ├── __init__.py
│   │   ├── orchestrator_node.py
│   │   ├── guardrails_node.py
│   │   └── synthesizer_node.py
│   │
│   ├── tools/                     # Tools for agent use
│   │   ├── __init__.py
│   │   ├── tool_registry.py       # Tool management
│   │   └── therapy_tools.py       # Therapy-specific tools
│   │
│   ├── workflows/                 # LangGraph workflows
│   │   ├── __init__.py
│   │   └── multi_agentic_workflow.py
│   │
│   ├── models/                    # Data models
│   │   ├── __init__.py
│   │   ├── models.py              # Core models
│   │   └── response_models.py     # Response formats
│   │
│   ├── config/                    # Configuration
│   │   ├── __init__.py
│   │   └── app_config.py
│   │
│   └── utils/                     # Utilities
│       ├── __init__.py
│       └── mood_detector.py
│
├── tests/                         # Test suite
│   ├── agents/
│   ├── workflows/
│   └── utils/
│
├── pyproject.toml
├── README.md
└── .env.example
```

## Workflow

```
User Message
     │
     ▼
Orchestrator (routes to appropriate therapy agent)
     │
     ├──> Positive Agent (for positive mood)
     ├──> Neutral Agent (for neutral mood)
     ├──> Negative Agent (for negative mood)
     └──> Problem Solver (for solutions)
     │
     ▼
Guardrails (safety check)
     │
     ▼
Synthesizer (polish response)
     │
     ▼
User Response
```

## Installation

```bash
# Clone the repository
cd encode

# Install dependencies using uv
uv sync

# Or install with pip
pip install -e .
```

## Configuration

1. Copy the environment example file:
```bash
cp .env.example .env
```

2. Add your API key:
```
OPENAI_API_KEY=your_key_here
# OR
GOOGLE_API_KEY=your_key_here
```

## Usage

### Interactive Session

```bash
# Using the installed script
encode

# Or run directly
python -m app.main
```

### Programmatic Usage

```python
from app.agents.agent_factory import create_multi_agent_workflow

# Create the workflow
workflow = create_multi_agent_workflow()

# Chat with the system
response = workflow.chat("Hello, I'm feeling anxious today")
print(response)

# Continue the conversation
response = workflow.chat("I have a big presentation tomorrow")
print(response)

# Reset the conversation
workflow.reset()
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/agents/test_orchestrator_agent.py
```

### Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type checking
mypy app/
```

## License

MIT