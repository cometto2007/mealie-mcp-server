# Mealie MCP Server Project

## Goal

Build a remote MCP server that exposes Mealie's recipe/meal planning API, deployable as a Docker container on Unraid, accessible as a custom connector in claude.ai (Settings → Connectors → Add custom connector).

## Background & Context

Chris runs an Unraid server with existing infrastructure:
- **Traefik** reverse proxy
- **Authelia** authentication
- **PostgreSQL** database container
- **Mealie** recipe/meal planning app (self-hosted)

The longer-term vision includes a custom **freezer inventory app** (Node.js/Express, PostgreSQL) that cross-references with Mealie to answer questions like "How long are we covered with dish X?" — but this MCP server is the first piece.

## Existing Mealie MCP Servers (Reference)

Two existing repos to learn from:

### 1. mdlopresti/mealie-mcp (Primary reference)
- **Repo:** https://github.com/mdlopresti/mealie-mcp
- **Stack:** Python 3.12+, FastMCP, has Dockerfile
- **Docker image:** `ghcr.io/mdlopresti/mealie-mcp:latest`
- **Tested with:** Mealie v3.6.1
- **Transport:** stdio only (needs HTTP transport added)
- **Tools:** recipes.py, mealplans.py, shopping.py
- **Structure:**
  ```
  mealie-mcp/
  ├── Dockerfile
  ├── requirements.txt
  ├── build.sh
  └── src/
      ├── server.py          # MCP server entry point
      ├── client.py          # Mealie API client
      ├── tools/
      │   ├── recipes.py
      │   ├── mealplans.py
      │   └── shopping.py
      └── resources/
          ├── recipes.py
          ├── mealplans.py
          └── shopping.py
  ```

### 2. rldiao/mealie-mcp-server (Secondary reference)
- **Repo:** https://github.com/rldiao/mealie-mcp-server
- **Stack:** Python 3.12+, FastMCP, uv package manager
- **Transport:** stdio only
- **Simpler implementation** — fewer features but cleaner to read

## Key Technical Decision: Transport

Both existing repos use **stdio** transport (designed for Claude Desktop local process). We need **Streamable HTTP** transport so it can be used as a remote MCP server URL in claude.ai.

### How Streamable HTTP works:
- Single `/mcp` endpoint handles POST and GET
- POST for sending JSON-RPC messages
- Optional SSE upgrade for streaming responses
- Replaces the older dual-endpoint SSE transport

### FastMCP makes this easy:
```python
from fastmcp import FastMCP

mcp = FastMCP("mealie-server")

# Register tools...

mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
```

Or for a stateless mode (better for horizontal scaling):
```python
mcp = FastMCP("mealie-server", stateless_http=True)
mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
```

The `/mcp` endpoint is then exposed through Traefik/Cloudflare Tunnel.

## Build Plan

### Phase 1: Fork & Add HTTP Transport
1. Fork `mdlopresti/mealie-mcp`
2. Update `server.py` to support streamable HTTP transport (keep stdio as fallback)
3. Update Dockerfile to expose the HTTP port
4. Test locally with Docker against Chris's Mealie instance

### Phase 2: Secure & Deploy
1. Deploy container on Unraid
2. Expose via **Cloudflare Tunnel** or **Tailscale** (preferred over opening ports)
3. Add to claude.ai: Settings → Connectors → Add custom connector → paste URL
4. Test from claude.ai — search recipes, check meal plans, manage shopping lists

### Phase 3: Freezer Inventory MCP (Future)
1. Build the freezer inventory Node.js/Express app
2. Build a second MCP server (or extend this one) for freezer data
3. Enable cross-referencing: "How many portions of lasagna in the freezer?" + "When is lasagna next on the meal plan?"

## Environment Variables

```
MEALIE_URL=https://your-mealie-instance.com
MEALIE_API_TOKEN=your-api-token-here
MCP_TRANSPORT=streamable-http    # or stdio
MCP_HOST=0.0.0.0
MCP_PORT=8000
```

## Auth Considerations

- Mealie API token: generated in Mealie → User Settings → API Tokens
- Consider creating a dedicated Mealie user for the MCP server
- The MCP server itself will sit behind Traefik/Authelia or Cloudflare Tunnel (handles external auth)
- claude.ai custom connectors support OAuth if needed

## Dev Environment

- **Editor:** Cursor (VS Code fork) with integrated terminal
- **CLI:** Claude Code (`brew install --cask claude-code`) running in Cursor's terminal
- **Docker:** Docker Desktop for Mac for local container testing
- **Python:** 3.12+ with uv package manager
- **Tunnel:** `cloudflared` CLI (`brew install cloudflared`) for exposing to internet

## Useful Commands

```bash
# Clone the reference repo
git clone https://github.com/mdlopresti/mealie-mcp.git
cd mealie-mcp

# Run locally (stdio mode for testing)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export MEALIE_URL=https://your-mealie-instance.com
export MEALIE_API_TOKEN=your-api-token
python -m src.server

# Build Docker image
docker build -t mealie-mcp:latest .

# Run Docker container
docker run -i --rm \
  -e MEALIE_URL=https://your-mealie-instance.com \
  -e MEALIE_API_TOKEN=your-api-token-here \
  -p 8000:8000 \
  mealie-mcp:latest

# Test the MCP endpoint
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}'
```

## Notes

- The MCP spec version we're targeting is `2025-03-26` (Streamable HTTP)
- FastMCP (Python) handles both SSE and Streamable HTTP with minimal config
- The claude.ai custom connector feature is in beta — things may change
- QR code system for freezer containers is a future nice-to-have for the inventory app
