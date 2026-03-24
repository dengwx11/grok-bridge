#!/usr/bin/env python3
"""
grok-bridge MCP Server
Exposes Grok AI as a Claude Code tool via the local grok-bridge REST API.
"""
import httpx
from mcp.server.fastmcp import FastMCP

BRIDGE_URL = "http://localhost:19998"
X_BRIDGE_URL = "http://localhost:19999"

mcp = FastMCP("grok-bridge")

def _call(method: str, path: str, base: str = BRIDGE_URL, **kwargs) -> dict:
    try:
        r = httpx.request(method, f"{base}{path}", timeout=120, trust_env=False, **kwargs)
        return r.json()
    except httpx.ConnectError:
        return {"status": "error", "error": f"Bridge server not running at {base}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool()
def grok_chat(prompt: str, timeout: int = 90) -> str:
    """Send a message to Grok AI and get a response. Uses Safari automation — Safari must be open and logged into grok.com."""
    result = _call("POST", "/chat", json={"prompt": prompt, "timeout": timeout})
    if result.get("status") == "ok":
        return result.get("response", "")
    return f"[Error] {result.get('error', 'unknown error')}"

@mcp.tool()
def grok_new_conversation() -> str:
    """Start a fresh Grok conversation (clears context)."""
    result = _call("POST", "/new")
    return "New conversation started." if result.get("status") == "ok" else f"[Error] {result.get('error')}"

@mcp.tool()
def x_grok_chat(prompt: str, timeout: int = 90) -> str:
    """Send a message to Grok on X (Twitter) and get a response. X Grok has real-time access to X posts, trending topics, and platform data. Use this when asking about X trends, viral posts, or anything requiring live X data."""
    result = _call("POST", "/chat", base=X_BRIDGE_URL, json={"prompt": prompt, "timeout": timeout})
    if result.get("status") == "ok":
        return result.get("response", "")
    return f"[Error] {result.get('error', 'unknown error')}"

@mcp.tool()
def x_grok_new_conversation() -> str:
    """Start a fresh conversation with Grok on X (clears context)."""
    result = _call("POST", "/new", base=X_BRIDGE_URL)
    return "New X Grok conversation started." if result.get("status") == "ok" else f"[Error] {result.get('error')}"

@mcp.tool()
def grok_health() -> str:
    """Check if grok-bridge is running and Safari is on grok.com."""
    result = _call("GET", "/health")
    if result.get("status") == "ok":
        return f"OK — Safari is at {result.get('url')} | on_grok={result.get('on_grok')}"
    return f"[Error] {result.get('error')}"

if __name__ == "__main__":
    mcp.run()
