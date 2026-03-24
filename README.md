# 🌉 grok-bridge v4.0

Turn **Grok** (grok.com or X/Twitter) into a REST API + Claude Code MCP tool. No API key needed.

Query Grok directly from Claude Code — including **X Grok** for real-time trending topics, live market sentiment, and breaking news from X/Twitter.

## How it works

```
Claude Code / HTTP Client → REST API → AppleScript → Safari JS injection → grok.com → DOM extraction
```

Two modes:

### REST API (recommended)
```bash
# Start the server on your Mac
python3 scripts/grok_bridge.py --port 19998

# Query from anywhere
curl -X POST http://localhost:19998/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"What is the mass of the sun?","timeout":60}'

# Health check
curl http://localhost:19998/health

# Read current conversation
curl http://localhost:19998/history
```

### CLI (legacy)
```bash
# Local
bash scripts/grok_chat.sh "Explain quantum tunneling"

# Remote via SSH
MAC_SSH="ssh user@your-mac" bash scripts/grok_chat.sh "Write a haiku" --timeout 90
```

## Requirements

- **macOS** with Safari
- **Python 3.10+**
- Logged into [grok.com](https://grok.com) (free or SuperGrok)
- **No Accessibility permission needed** (v3 uses JS injection, not System Events)

### Safari Setup (required)

**Step 1** — Enable the Develop menu:
> Safari → Settings → Advanced → check **"Show features for web developers"**

**Step 2** — Allow JavaScript from Apple Events:
> Safari → Develop → check **"Allow JavaScript from Apple Events"**

## Claude Code Skill (`/grok-bridge`)

Install as a Claude Code skill to invoke with `/grok-bridge`:

```bash
mkdir -p ~/.claude/skills/grok-bridge
cp SKILL.md ~/.claude/skills/grok-bridge/SKILL.md
```

Then in Claude Code, type `/grok-bridge` followed by your question. Claude will automatically route it to the right Grok endpoint (grok.com or X Grok).

> **Requires** the MCP server to be registered and bridge servers running (see below).

## Claude Code (MCP)

This repo includes an MCP server (`mcp_server.py`) that exposes Grok as tools inside Claude Code.

### Install dependencies
```bash
pip install mcp httpx
```

### Register the MCP server
```bash
claude mcp add grok-bridge python3 /path/to/grok-bridge/mcp_server.py
```

Or add to `~/.claude/settings.json` manually:
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

### Available tools

| Tool | Description |
|------|-------------|
| `grok_chat` | Send a prompt to Grok on grok.com |
| `grok_new_conversation` | Start a fresh conversation on grok.com |
| `x_grok_chat` | Send a prompt to Grok on X (real-time X data) |
| `x_grok_new_conversation` | Start a fresh conversation on X |
| `grok_health` | Check if the bridge server is running |

> **Note:** Start the REST API server(s) before using Claude Code tools.
> For X Grok: `python3 scripts/x_grok_bridge.py --port 19999`

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/chat` | Send prompt, wait for response |
| POST | `/new` | Start new conversation |
| GET | `/health` | Health check (Safari URL, grok status) |
| GET | `/history` | Read current page conversation |

## Troubleshooting

**`Bridge server not running`**
→ Start the server first: `python3 scripts/grok_bridge.py`

**`Allow JavaScript from Apple Events` is greyed out**
→ You must first enable "Show features for web developers" in Safari → Settings → Advanced.

**Safari is not on grok.com**
→ Open Safari and navigate to [grok.com](https://grok.com) manually before querying.

**Timeout errors**
→ Increase the timeout parameter: `{"prompt": "...", "timeout": 120}`

**Response is cut off or empty**
→ Grok may still be generating. Retry with a higher timeout or start a new conversation (`POST /new`).

## Version History

| | v1 | v2 | v3 |
|---|---|---|---|
| Input | Peekaboo UI | pbcopy + Cmd+V | JS `execCommand('insertText')` |
| Submit | UI click | System Events Return | JS `button.click()` |
| Permissions | Peekaboo + Accessibility | Accessibility | **None** (pure JS injection) |
| Interface | CLI only | CLI only | **REST API** + CLI |
| Dependencies | Peekaboo (brew) | None | None (stdlib only) |
| Speed | ~30s | ~3s | ~3s |

## Architecture

```
┌──────────────┐                     ┌───────────────────────┐
│  HTTP Client │  POST /chat         │      macOS            │
│  (anywhere)  │ ──────────────────→ │                       │
└──────────────┘                     │  grok_bridge.py       │
                                     │  ↓ osascript          │
                                     │  Safari do JavaScript │
                                     │  ↓ execCommand        │
                                     │  grok.com textarea    │
                                     │  ↓ button.click()     │
                                     │  Grok responds        │
                                     │  ↓ DOM poll           │
                                     │  Response extracted   │
                                     └───────────────────────┘
```

## Key Insight (v3)

React controlled inputs ignore JavaScript `value` setter, synthetic `InputEvent`, and even `nativeInputValueSetter`.

What **doesn't** work from SSH:
- ❌ `osascript keystroke` — blocked by macOS Accessibility
- ❌ CGEvent (Swift) — HID events don't reach web content
- ❌ JS `InputEvent` / `nativeInputValueSetter` — React ignores synthetic events

What **does** work:
- ✅ `document.execCommand('insertText')` — triggers real input in the browser
- ✅ JS `button.click()` on Send button — no System Events needed

Zero permissions, zero dependencies, pure JavaScript injection via AppleScript.

## Credits

Forked from [ythx-101/grok-bridge](https://github.com/ythx-101/grok-bridge).
MCP server and X Grok support added by [dengwx11](https://github.com/dengwx11).

## License

MIT
