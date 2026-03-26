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
  - Bash

---

## How to use this skill

Send the user's question directly to Grok on X using `x_grok_chat`.

### 步骤 0：确保 Safari 就绪（每次调用前执行）

1. 调用 `grok_health` 检查状态：
   - 如果返回错误（包含 "Invalid index" / "Can't get window" / "Error"）：
     Safari 未开启，执行：
     ```bash
     open -a Safari "https://x.com/i/grok"
     sleep 4
     ```
     然后调用 `x_grok_new_conversation`，再继续。
   - 如果返回 `on_grok=False`：
     Safari 开着但不在 x.com/i/grok，调用 `x_grok_new_conversation` 导航过去，再继续。
   - 如果返回 `on_grok=True` 或 URL 包含 x.com/i/grok：
     直接继续，无需额外操作。

2. 如果 `x_grok_new_conversation` 也失败（bridge 服务未启动），提示用户：
   ```bash
   python3 scripts/x_grok_bridge.py --port 19999
   ```

### 步骤 1：发送问题

1. Pass the user's question as-is to `x_grok_chat`. Keep it in the user's language.
2. Return Grok's response directly.
3. Default timeout is 90 seconds. For complex questions, pass `timeout: 120`.
4. Use `x_grok_new_conversation` if context from a previous session is interfering.
