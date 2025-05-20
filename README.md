# local-mcp-server

A demo local MCP Server to experiment things out.

## Creating a Python MCP Server
```bash
uv init mcp-server-1
cd mcp-server-1
uv add "mcp[cli]"
uv add psycopg2
```

## Running the MCP Server in Claude Desktop
uv run mcp install main.py
uv run mcp install main.py -f .env

## Running the MCP Server in dev mode
POSTGRES_USER=postgres POSTGRES_PASSWORD=postgres uv run mcp dev main.py
