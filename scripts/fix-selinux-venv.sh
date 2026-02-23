#!/bin/bash
# Fix SELinux so systemd (init_t) can execute the Gunicorn venv when the service
# runs from a directory under /home (user_home_t). Run on the server with sudo.
#
# Usage (on server):
#   sudo bash fix-selinux-venv.sh
# Or from repo root over SSH:
#   ssh bayoupal 'sudo bash -s' < scripts/fix-selinux-venv.sh
#
# Requires: policycoreutils-python-utils (semanage), policycoreutils (restorecon)

set -e
APP_DIR="${APP_DIR:-/home/ccastille/hsirb-system}"
VENV_BIN="${APP_DIR}/venv/bin"

if [[ ! -d "$VENV_BIN" ]]; then
  echo "Venv not found at $VENV_BIN. Set APP_DIR if different (e.g. APP_DIR=/home/ccastille/hsirb-system)."
  exit 1
fi

# Allow systemd to execute binaries in this venv by labeling them as bin_t
if command -v semanage &>/dev/null; then
  if ! semanage fcontext -l | grep -q "${VENV_BIN}"; then
    semanage fcontext -a -t bin_t "${VENV_BIN}(/.*)?"
    echo "Added SELinux fcontext for ${VENV_BIN}"
  else
    echo "SELinux fcontext already exists for ${VENV_BIN}"
  fi
  restorecon -Rv "$VENV_BIN"
  echo "Restored contexts on ${VENV_BIN}"
else
  echo "semanage not found. Install policycoreutils-python-utils and run again."
  exit 1
fi

echo "Done. Restart the app service: sudo systemctl restart hsirb-system"
