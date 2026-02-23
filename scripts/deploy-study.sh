#!/bin/bash
# Deploy a specific study to bayoupal: pull code, migrate, collectstatic, run study command(s).
# Usage: ./scripts/deploy-study.sh <study-slug>
# Example: ./scripts/deploy-study.sh whole-person-fit
# Study slugs and commands are in config/deployable_studies.txt

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG="$REPO_ROOT/config/deployable_studies.txt"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

STUDY_SLUG="${1:-}"

if [ -z "$STUDY_SLUG" ]; then
    echo -e "${RED}Usage: $0 <study-slug>${NC}"
    echo "Available study slugs (from config/deployable_studies.txt):"
    grep -v '^#' "$CONFIG" | grep -v '^$' | cut -d: -f1 | sed 's/^/  - /'
    exit 1
fi

# Get command(s) for this slug (skip comments and empty lines)
COMMANDS=$(grep -v '^#' "$CONFIG" | grep -v '^$' | grep "^${STUDY_SLUG}:" | head -1 | cut -d: -f2-)
if [ -z "$COMMANDS" ]; then
    echo -e "${RED}Unknown study slug: ${STUDY_SLUG}${NC}"
    echo "Available:"
    grep -v '^#' "$CONFIG" | grep -v '^$' | cut -d: -f1 | sed 's/^/  - /'
    exit 1
fi

echo -e "${GREEN}🚀 Deploying study: ${STUDY_SLUG} to bayoupal.nicholls.edu${NC}\n"
echo -e "${BLUE}Commands to run: ${COMMANDS}${NC}\n"

# Run on server: pull, migrate, collectstatic, then each management command
# Pass COMMANDS via remote env (ssh doesn't forward local env)
ssh bayoupal "DEPLOY_STUDY_COMMANDS='$COMMANDS' bash -s" << 'REMOTE'
    set -e
    cd ~/hsirb-system
    echo "📦 Pulling latest..."
    git fetch origin
    git reset --hard origin/main
    source venv/bin/activate
    pip install -q -r requirements.txt
    echo "🔄 Migrating..."
    python manage.py migrate --noinput
    echo "📁 Collecting static..."
    python manage.py collectstatic --noinput --no-color 2>/dev/null || true
    IFS=',' read -ra CMDS <<< "$DEPLOY_STUDY_COMMANDS"
    for cmd in "${CMDS[@]}"; do
        cmd=$(echo "$cmd" | xargs)
        [ -z "$cmd" ] && continue
        echo "▶ Running: python manage.py $cmd"
        python manage.py $cmd
    done
    echo "✅ Study deploy complete."
REMOTE

echo -e "\n${GREEN}✅ Done.${NC} Test at https://bayoupal.nicholls.edu/hsirb/"
