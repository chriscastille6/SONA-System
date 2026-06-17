#!/bin/bash
# Deploy from your local repo (e.g. GitHub PRAMS) to bayoupal via rsync.
# No git pull on the server - use this when server→GitLab/GitHub is slow or broken.
#
# Usage: run from repo root on your Mac:
#   ./deploy-to-server-rsync.sh
#   ./deploy-to-server-rsync.sh --skip-populate   # skip populate_goal_setting_protocol_details
#
# Requires: rsync, ssh access to bayoupal. Server keeps its own .git and venv;
# we only sync application code and then run migrate/collectstatic/restart.

set -e
SKIP_POPULATE=false
for arg in "$@"; do
  case "$arg" in
    --skip-populate) SKIP_POPULATE=true ;;
  esac
done

SERVER_USER="ccastille"
SERVER_HOST="bayoupal.nicholls.edu"
REMOTE_PATH="hsirb-system"
# Repo root (directory containing manage.py)
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Deploying from $REPO_ROOT to ${SERVER_USER}@${SERVER_HOST}:~/${REMOTE_PATH}/"
echo "Syncing code (excluding .git, virtualenvs, staticfiles, media, db)..."
rsync -avz --delete \
  --exclude='.git' \
  --exclude='venv' \
  --exclude='.venv' \
  --exclude='venv312' \
  --exclude='tmp' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='staticfiles' \
  --exclude='media' \
  --exclude='db.sqlite3' \
  --exclude='.env' \
  --exclude='node_modules' \
  "$REPO_ROOT/" "${SERVER_USER}@${SERVER_HOST}:~/${REMOTE_PATH}/"

if [ "$SKIP_POPULATE" = true ]; then
  echo "Running migrate, collectstatic, cleanup, restart on server (--skip-populate)..."
  POPULATE_CMD=""
else
  echo "Running migrate, collectstatic, populate_protocol, cleanup, restart on server..."
  POPULATE_CMD="python manage.py populate_goal_setting_protocol_details && "
fi
ssh "${SERVER_USER}@${SERVER_HOST}" "cd ~/${REMOTE_PATH} && source venv/bin/activate && python manage.py migrate --noinput && python manage.py collectstatic --noinput && ${POPULATE_CMD}python manage.py cleanup_test_studies && echo 'Restarting app...' && (sudo systemctl restart hsirb-system 2>/dev/null || true)"
echo "Done. Test: https://bayoupal.nicholls.edu/hsirb/"
echo "If restart failed, SSH in and run: sudo systemctl restart hsirb-system"
