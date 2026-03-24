---
name: x-grok
version: 4.0.0
description: |
  Query Grok on X/Twitter via Safari automation — no API key needed.
  X Grok has real-time access to X posts, trending topics, live market sentiment,
  breaking news, and viral content. Use this when the user asks about X trends,
  stock market buzz, current events, or anything requiring live data from X.
  For general questions without X data, use the /grok-bridge skill instead.
allowed-tools:
  - mcp__grok-bridge__x_grok_chat
  - mcp__grok-bridge__x_grok_new_conversation
  - mcp__grok-bridge__grok_health

---

## How to use this skill

Send the user's question directly to Grok on X using `x_grok_chat`.

1. Pass the user's question as-is to `x_grok_chat`. Keep it in the user's language.
2. If you get a connection error, tell the user to start the X bridge server:
   ```bash
   python3 scripts/x_grok_bridge.py --port 19999
   ```
   And make sure Safari is open and logged into [x.com](https://x.com).
3. Return Grok's response directly.
4. Default timeout is 90 seconds. For complex questions, pass `timeout: 120`.
5. Use `x_grok_new_conversation` if context from a previous session is interfering.
