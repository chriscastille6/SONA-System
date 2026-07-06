#!/usr/bin/env bash
# Push approved PRAMS updates to institutional GitLab.
# Use after local review; GitLab CI deploys from main after you approve the pipeline.
set -euo pipefail

GITLAB_REMOTE="${GITLAB_REMOTE:-gitlab}"
GITLAB_URL="${GITLAB_URL:-git@gitlab.nicholls.edu:chriscastille/prams.git}"
BRANCH="${1:-$(git branch --show-current)}"

if ! git remote get-url "${GITLAB_REMOTE}" >/dev/null 2>&1; then
  echo "Adding GitLab remote '${GITLAB_REMOTE}' → ${GITLAB_URL}"
  git remote add "${GITLAB_REMOTE}" "${GITLAB_URL}"
fi

echo "Pushing branch '${BRANCH}' to ${GITLAB_REMOTE}..."
git push -u "${GITLAB_REMOTE}" "${BRANCH}"

echo ""
echo "Next steps:"
echo "  1. Open a merge request on GitLab: ${GITLAB_URL%.git}/-/merge_requests/new"
echo "  2. Wait for CI validate + test to pass."
echo "  3. Approve and merge to main."
echo "  4. In GitLab CI/CD → Pipelines, click Play on deploy:production."
