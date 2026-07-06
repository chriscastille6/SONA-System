# PRAMS MCP data layer

Universal SQL access for PRAMS agents via **MindsDB** + **Google MCP Toolbox for Databases**.

## Quick start

```bash
cp config/mcp/env.mcp.template config/mcp/.env
# Edit config/mcp/.env — at minimum set GITLAB_API_KEY for GitLab federation

./scripts/mcp-start.sh
```

Enable the `prams-mindsdb` server in Cursor (`.cursor/mcp.json`), then use MCP tools:

- `mindsdb-execute-sql` — run SQL across PRAMS PostgreSQL, GitLab, and future sources
- `mindsdb-sql` — parameterized SQL

## What gets connected

| MindsDB database | Source | Requires |
|------------------|--------|----------|
| `prams_postgres` | PRAMS app PostgreSQL | `PRAMS_POSTGRES_*` in `.env` |
| `prams_gitlab` | GitLab MRs + issues | `GITLAB_API_KEY` |

Add Gmail, Slack, S3, Salesforce, etc. with additional `CREATE DATABASE` statements — see [MCP_DATA_LAYER.md](../../docs/MCP_DATA_LAYER.md).

## Example queries

See [example-queries.sql](./example-queries.sql).
