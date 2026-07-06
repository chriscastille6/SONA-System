#!/usr/bin/env bash
# Register PRAMS federated data sources in MindsDB via HTTP API.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${MCP_ENV_FILE:-$ROOT/config/mcp/.env}"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
elif [[ -f "$ROOT/config/mcp/env.mcp.template" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ROOT/config/mcp/env.mcp.template"
  set +a
fi

MINDSDB_HTTP="${MINDSDB_HTTP:-http://${MINDSDB_HOST:-127.0.0.1}:${MINDSDB_HTTP_PORT:-47334}}"
MAX_ATTEMPTS="${MCP_BOOTSTRAP_ATTEMPTS:-60}"

run_sql() {
  local query="$1"
  curl -sf -X POST "${MINDSDB_HTTP}/api/sql/query" \
    -H "Content-Type: application/json" \
    -d "$(python3 -c 'import json,sys; print(json.dumps({"query": sys.stdin.read()}))' <<<"$query")"
  echo ""
}

wait_for_mindsdb() {
  echo "Waiting for MindsDB at ${MINDSDB_HTTP}..."
  for i in $(seq 1 "$MAX_ATTEMPTS"); do
    if curl -sf "${MINDSDB_HTTP}/api/status" >/dev/null 2>&1; then
      echo "MindsDB is ready."
      return 0
    fi
    sleep 2
  done
  echo "MindsDB did not become ready in time." >&2
  return 1
}

bootstrap_postgres() {
  local host="${PRAMS_POSTGRES_HOST:-host.docker.internal}"
  local port="${PRAMS_POSTGRES_PORT:-5432}"
  local db="${PRAMS_POSTGRES_DATABASE:-recruitment_db}"
  local user="${PRAMS_POSTGRES_USER:-postgres}"
  local pass="${PRAMS_POSTGRES_PASSWORD:-postgres}"

  echo "Connecting PRAMS PostgreSQL → prams_postgres..."
  run_sql "CREATE DATABASE IF NOT EXISTS prams_postgres
WITH ENGINE = 'postgres',
PARAMETERS = {
  \"host\": \"${host}\",
  \"port\": ${port},
  \"database\": \"${db}\",
  \"user\": \"${user}\",
  \"password\": \"${pass}\"
};"
}

bootstrap_gitlab() {
  if [[ -z "${GITLAB_API_KEY:-}" ]]; then
    echo "Skipping GitLab (set GITLAB_API_KEY in config/mcp/.env to enable)."
    return 0
  fi

  local url="${GITLAB_URL:-https://gitlab.nicholls.edu}"
  local repo="${GITLAB_REPOSITORY:-chriscastille/prams}"

  echo "Connecting GitLab ${repo} → prams_gitlab..."
  run_sql "CREATE DATABASE IF NOT EXISTS prams_gitlab
WITH ENGINE = 'gitlab',
PARAMETERS = {
  \"repository\": \"${repo}\",
  \"api_key\": \"${GITLAB_API_KEY}\",
  \"url\": \"${url}\"
};"
}

main() {
  wait_for_mindsdb
  bootstrap_postgres
  bootstrap_gitlab
  echo "Bootstrap complete. Connected sources:"
  run_sql "SHOW DATABASES;"
}

main "$@"
