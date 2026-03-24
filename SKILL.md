# grok-bridge

Use this skill to query Grok (on grok.com or X/Twitter) through Safari automation — no API key required.

## How It Works

```
Claude Code → MCP server → HTTP → localhost REST API → AppleScript → Safari JS → grok.com
```

- Safari `do JavaScript` via AppleScript (no Chrome DevTools needed)
- `document.execCommand('insertText')` to type into React-controlled inputs
- `button.click()` to submit — no Accessibility permission required

## Prerequisites

### 1. macOS + Safari
Safari must be open and logged into [grok.com](https://grok.com) (free account works; SuperGrok recommended for longer responses).

### 2. Enable Safari Developer Features

**Step 1** — Enable the Develop menu:
> Safari → Settings → Advanced → check **"Show features for web developers"**

**Step 2** — Allow JavaScript from Apple Events:
> Safari → Develop → check **"Allow JavaScript from Apple Events"**

### 3. Python 3.10+
```bash
python3 --version  # must be 3.10 or later
```

### 4. Install MCP dependency
```bash
pip install mcp httpx
```

## Setup: Register as Claude Code MCP

```bash
claude mcp add grok-bridge python3 /path/to/grok-bridge/mcp_server.py
```

Or add manually to your Claude Code settings (`~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "grok-bridge": {
      "command": "python3",
      "args": ["/path/to/grok-bridge/mcp_server.py"]
    }
  }
}
```

## Start the Bridge Servers

You must start the REST API server(s) before using the MCP tools:

```bash
# For grok.com (port 19998)
python3 scripts/grok_bridge.py --port 19998

# For X/Twitter Grok (port 19999)
python3 scripts/x_grok_bridge.py --port 19999
```

Keep these running in the background while using Claude Code.

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `grok_chat` | Send a prompt to Grok on grok.com |
| `grok_new_conversation` | Start a fresh conversation on grok.com |
| `x_grok_chat` | Send a prompt to Grok on X (real-time X data access) |
| `x_grok_new_conversation` | Start a fresh conversation on X |
| `grok_health` | Check if the bridge server is running |

## REST API (Direct Use)

```bash
# Send a prompt
curl -X POST http://localhost:19998/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the capital of France?", "timeout": 60}'

# Health check
curl http://localhost:19998/health

# Start new conversation
curl -X POST http://localhost:19998/new
```

## Troubleshooting

**Bridge not running:**
> `[Error] Bridge server not running at http://localhost:19998`
→ Start the server: `python3 scripts/grok_bridge.py`

**Safari not at grok.com:**
→ Open Safari and navigate to [grok.com](https://grok.com) manually.

**"Allow JavaScript from Apple Events" not available:**
→ You must first enable "Show features for web developers" in Safari → Settings → Advanced.

**Timeout errors:**
→ Increase the timeout: `{"prompt": "...", "timeout": 120}`

## Credits

Forked from [ythx-101/grok-bridge](https://github.com/ythx-101/grok-bridge).
MCP server and X Grok support added by [dengwx11](https://github.com/dengwx11).
