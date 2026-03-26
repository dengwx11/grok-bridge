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
  - Bash

---

## How to use this skill

Send the user's question directly to Grok on grok.com using `grok_chat`.

### 步骤 0：确保 Safari 就绪（每次调用前执行）

1. 调用 `grok_health` 检查状态：
   - 如果返回错误（包含 "Invalid index" / "Can't get window" / "Error"）：
     Safari 未开启，执行：
     ```bash
     open -a Safari "https://grok.com"
     sleep 4
     ```
     然后调用 `grok_new_conversation`，再继续。
   - 如果返回 `on_grok=False`：
     Safari 开着但不在 grok.com，调用 `grok_new_conversation` 导航过去，再继续。
   - 如果返回 `on_grok=True` 或 URL 包含 grok.com：
     直接继续，无需额外操作。

2. 如果 `grok_new_conversation` 也失败（bridge 服务未启动），提示用户：
   ```bash
   python3 scripts/grok_bridge.py --port 19998
   ```

### 步骤 1：发送问题

1. Pass the user's question as-is to `grok_chat`. Keep it in the user's language.
2. Return Grok's response directly.
3. Default timeout is 90 seconds. For complex questions, pass `timeout: 120`.
4. Use `grok_new_conversation` if context from a previous session is interfering.
