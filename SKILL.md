---
name: grok-bridge
version: 4.0.0
description: |
  Query Grok AI on grok.com via Safari automation — no API key needed.
  Use for general questions, reasoning, coding help, research, and anything
  that does not require real-time X/Twitter data. For live X trends or posts,
  use the /x-grok skill instead.
allowed-tools:
  - mcp__grok-bridge__grok_chat
  - mcp__grok-bridge__grok_new_conversation
  - mcp__grok-bridge__grok_health

---

## How to use this skill

Send the user's question directly to Grok on grok.com using `grok_chat`.

1. Pass the user's question as-is to `grok_chat`. Keep it in the user's language.
2. If you get a connection error, tell the user to start the bridge server:
   ```bash
   python3 scripts/grok_bridge.py --port 19998
   ```
   And make sure Safari is open and logged into [grok.com](https://grok.com).
3. Return Grok's response directly.
4. Default timeout is 90 seconds. For complex questions, pass `timeout: 120`.
5. Use `grok_new_conversation` if context from a previous session is interfering.
