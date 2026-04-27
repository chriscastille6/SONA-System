#!/bin/bash
# Deploy from your local repo (e.g. GitHub SONA System) to bayoupal via rsync.
# No git pull on the server - use this when server→GitLab/GitHub is slow or broken.
#
# Usage: run from repo root on your Mac:
#   ./deploy-to-server-rsync.sh
#
# Requires: rsync, ssh access to bayoupal. Server keeps its own .git and venv;
# we only sync application code and then run migrate/collectstatic/restart.

set -e
SERVER_USER="ccastille"
SERVER_HOST="bayoupal.nicholls.edu"
REMOTE_PATH="hsirb-system"
# Repo root (directory containing manage.py)
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Deploying from $REPO_ROOT to ${SERVER_USER}@${SERVER_HOST}:~/${REMOTE_PATH}/"
echo "Syncing code (excluding .git, venv, staticfiles, media, db)..."
rsync -avz --delete \
  --exclude='.git' \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='staticfiles' \
  --exclude='media' \
  --exclude='db.sqlite3' \
  --exclude='.env' \
  --exclude='node_modules' \
  "$REPO_ROOT/" "${SERVER_USER}@${SERVER_HOST}:~/${REMOTE_PATH}/"

echo "Running migrate, collectstatic, restart on server..."
ssh "${SERVER_USER}@${SERVER_HOST}" "cd ~/${REMOTE_PATH} && source venv/bin/activate && python manage.py migrate --noinput && python manage.py collectstatic --noinput && echo 'Restarting app...' && (sudo systemctl restart hsirb-system 2>/dev/null || true)"
echo "Done. Test: https://bayoupal.nicholls.edu/hsirb/"
echo "If restart failed, SSH in and run: sudo systemctl restart hsirb-system"
