# Conversation Data Storage

This directory stores conversation history files in JSON format.

Each conversation is stored as a separate JSON file with the naming pattern:
`{conversation_id}.json`

## File Format

```json
{
  "conversation_id": "session_123",
  "created_at": "2026-01-25T10:00:00",
  "updated_at": "2026-01-25T10:05:00",
  "messages": [
    {
      "role": "user",
      "content": "Hello, I'm feeling anxious",
      "timestamp": "2026-01-25T10:00:00"
    },
    {
      "role": "assistant",
      "content": "I hear you...",
      "timestamp": "2026-01-25T10:00:05"
    }
  ],
  "metadata": {
    "user_mood": "negative",
    "user_intent": "talk"
  }
}
```

## Notes

- Files are automatically created when conversations start
- Add `*.json` files here to `.gitignore` if you don't want to track conversations
- The `.gitkeep` file ensures this directory is tracked by git
