# Mealie MCP Server

A remote MCP server that exposes the [Mealie](https://mealie.io) recipe and meal planning API, deployable as a Docker container and accessible as a custom connector in [claude.ai](https://claude.ai).

## Features

- **Recipes** — search, get, create, update, delete recipes
- **Recipe Import** — import recipes from URLs using Mealie's built-in scraper
- **Nutrition** — update recipe nutrition data (calories, protein, carbs, fat, fiber, sodium, sugar, etc.)
- **Foods & Units** — list, search, and create ingredient foods and measurement units
- **Ingredient Parsing** — parse natural language ingredient strings into structured data
- **Meal Plans** — view today's plan, query by date range, create/delete entries
- **Shopping Lists** — manage lists and add items

## Transport

Uses **Streamable HTTP** transport (MCP spec `2025-03-26`) so it can be used as a remote MCP server URL in claude.ai → Settings → Connectors → Add custom connector.

Stdio transport is also supported for local Claude Desktop use.

## Setup

### Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Description | Default |
|---|---|---|
| `MEALIE_URL` | Your Mealie instance URL | required |
| `MEALIE_API_TOKEN` | Mealie API token (User Settings → API Tokens) | required |
| `MCP_TRANSPORT` | `streamable-http` or `stdio` | `streamable-http` |
| `MCP_HOST` | Host to bind to | `0.0.0.0` |
| `MCP_PORT` | Port to listen on | `8000` |

### Run with Docker

```bash
docker build -t mealie-mcp-server .

docker run -d \
  -e MEALIE_URL=https://your-mealie-instance.com \
  -e MEALIE_API_TOKEN=your-api-token \
  -p 8000:8000 \
  mealie-mcp-server
```

### Run locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m src.server
```

## Connecting to claude.ai

1. Deploy the container and expose port 8000 via Cloudflare Tunnel or similar
2. In claude.ai: Settings → Connectors → Add custom connector
3. Enter your MCP server URL: `https://your-tunnel-url.com/mcp`

## Testing

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}'
```

## Credits

Inspired by [mdlopresti/mealie-mcp](https://github.com/mdlopresti/mealie-mcp) and [rldiao/mealie-mcp-server](https://github.com/rldiao/mealie-mcp-server).
