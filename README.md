---
title: Aura - Multi-Agent Therapy System
emoji: ❤️
colorFrom: pink
colorTo: purple
sdk: gradio
sdk_version: 6.5.1
app_file: app.py
pinned: false
---

# ❤️ Aura - Multi-Agent Therapy System

A therapeutic support platform using LangGraph and Gradio for voice-based interactions.

## Features

- 🎤 Voice input support
- 🔊 Text-to-speech responses
- 🤖 Multi-agent workflow powered by LangGraph
- 💬 Interactive chat interface

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
1. Add your API key in .env:
```
OPENAI_API_KEY=your_key_here
# OR
GOOGLE_API_KEY=your_key_here
```

## Usage

### Run using

```
python app.py
```

## Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type checking
mypy app/
```