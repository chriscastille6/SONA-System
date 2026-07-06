-- PRAMS cross-source example queries (run via mindsdb-execute-sql MCP tool)
-- Requires scripts/mcp-bootstrap.sh to have created the federated databases.

-- 1. List connected MindsDB data sources
SHOW DATABASES;

-- 2. Open GitLab merge requests for PRAMS repo
SELECT id, title, state, author, created_at
FROM prams_gitlab.merge_requests
WHERE state = 'opened'
ORDER BY created_at DESC
LIMIT 20;

-- 3. Open GitLab issues
SELECT id, title, state, labels, created_at
FROM prams_gitlab.issues
WHERE state = 'opened'
ORDER BY created_at DESC
LIMIT 20;

-- 4. Cross-source join: studies + open MRs mentioning study slug (conceptual)
-- Adjust table/column names to match your PRAMS schema.
SELECT
  s.id AS study_id,
  s.title AS study_title,
  mr.title AS mr_title,
  mr.state AS mr_state
FROM prams_postgres.studies_study s
JOIN prams_gitlab.merge_requests mr
  ON mr.description LIKE CONCAT('%', s.slug, '%')
WHERE mr.state = 'opened';

-- 5. IRB protocol submissions pending review (PRAMS only)
SELECT id, title, status, submitted_at
FROM prams_postgres.studies_protocolsubmission
WHERE status IN ('submitted', 'under_review')
ORDER BY submitted_at DESC
LIMIT 20;

-- 6. Agent-safe participant view (no direct PII — use anonymized export patterns)
-- Prefer Django export commands for FERPA-compliant extracts; this is illustrative.
SELECT study_id, COUNT(*) AS signup_count
FROM prams_postgres.studies_signup
GROUP BY study_id;
