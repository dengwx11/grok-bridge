---
name: grok-bridge
version: 4.0.0
description: |
  Query Grok AI (grok.com or X/Twitter) via Safari automation — no API key needed.
  Use grok_chat for general questions, x_grok_chat for anything requiring real-time
  X/Twitter data (trending topics, viral posts, live market sentiment, breaking news).
  Requires the grok-bridge MCP server and REST bridge server to be running locally.
allowed-tools:
  - mcp__grok-bridge__grok_chat
  - mcp__grok-bridge__grok_new_conversation
  - mcp__grok-bridge__x_grok_chat
  - mcp__grok-bridge__x_grok_new_conversation
  - mcp__grok-bridge__grok_health

---

## How to use this skill

You have access to Grok AI through the grok-bridge MCP. Choose the right tool:

- **`x_grok_chat`** — use when the user asks about X/Twitter trends, live news, stock market sentiment, viral posts, or anything requiring real-time data from X.
- **`grok_chat`** — use for general questions, reasoning, coding help, or anything that doesn't need live X data.
- **`grok_health`** — check if the bridge server is running before attempting a query.

## Workflow

1. If the user's request needs real-time X data → use `x_grok_chat`
2. Otherwise → use `grok_chat`
3. If you get a connection error → tell the user to start the bridge server:
   ```bash
   python3 scripts/grok_bridge.py --port 19998      # for grok.com
   python3 scripts/x_grok_bridge.py --port 19999    # for X Grok
   ```
4. Pass the user's question directly as the `prompt` parameter. Keep it in the user's language.
5. Return Grok's response directly without heavy reformatting unless the user asks for it.

## Notes

- Default timeout is 90 seconds. For complex questions, pass `timeout: 120`.
- Safari must be open and logged into grok.com / x.com for the bridge to work.
- Start a new conversation with `grok_new_conversation` / `x_grok_new_conversation` if context from a previous session is interfering.
