#!/usr/bin/env bash
# Start MindsDB and bootstrap federated sources for PRAMS agents.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -f config/mcp/.env ]]; then
  echo "Creating config/mcp/.env from template (edit secrets before production use)."
  cp config/mcp/env.mcp.template config/mcp/.env
fi

echo "Starting MindsDB stack..."
docker compose -f docker-compose.mcp.yml up -d

echo "Bootstrapping federated data sources..."
bash "$ROOT/scripts/mcp-bootstrap.sh"

cat <<'EOF'

PRAMS MCP data layer is running.

  MindsDB editor:  http://127.0.0.1:47334
  MySQL API:       127.0.0.1:47335  (user: mindsdb, no password)

Cursor MCP: enable "prams-mindsdb" in .cursor/mcp.json (uses Google MCP Toolbox prebuilt=mindsdb).

Example queries: config/mcp/example-queries.sql
Docs: docs/MCP_DATA_LAYER.md

EOF
