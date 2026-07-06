#!/usr/bin/env bash
# GitLab CI deploy script — runs on bayoupal via SSH after manual approval.
set -euo pipefail

: "${DEPLOY_HOST:?Set DEPLOY_HOST CI variable}"
: "${DEPLOY_USER:?Set DEPLOY_USER CI variable}"
DEPLOY_PATH="${DEPLOY_PATH:-~/hsirb-system}"
GIT_REPO="${GIT_REPO:-git@gitlab.nicholls.edu:chriscastille/prams.git}"
GIT_BRANCH="${GIT_BRANCH:-main}"

echo "Deploying PRAMS to ${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_PATH}"

ssh -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=yes \
  "${DEPLOY_USER}@${DEPLOY_HOST}" \
  "DEPLOY_PATH='${DEPLOY_PATH}' GIT_REPO='${GIT_REPO}' GIT_BRANCH='${GIT_BRANCH}' bash -s" <<'REMOTE'
set -euo pipefail

mkdir -p "${DEPLOY_PATH}"
cd "${DEPLOY_PATH}"

if [ ! -d ".git" ]; then
  echo "Cloning ${GIT_REPO}..."
  git clone "${GIT_REPO}" "${DEPLOY_PATH}"
  cd "${DEPLOY_PATH}"
else
  echo "Pulling latest from ${GIT_BRANCH}..."
  git remote set-url origin "${GIT_REPO}"
  git fetch origin "${GIT_BRANCH}"
  git checkout "${GIT_BRANCH}"
  git pull origin "${GIT_BRANCH}"
fi

if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

python manage.py migrate --noinput
python manage.py collectstatic --noinput

if systemctl is-active --quiet hsirb-system 2>/dev/null; then
  sudo systemctl restart hsirb-system
  echo "Restarted hsirb-system service."
else
  echo "hsirb-system not running as systemd unit; restart Gunicorn manually if needed."
fi

echo "PRAMS deploy complete."
REMOTE

echo "Done. Verify: https://bayoupal.nicholls.edu/hsirb/"
