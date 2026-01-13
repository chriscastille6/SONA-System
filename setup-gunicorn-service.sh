#!/bin/bash
# File location: setup-gunicorn-service.sh
# What this file does: Sets up Gunicorn as a systemd service for HSIRB

# ============================================================================
# CONFIGURATION
# ============================================================================
SERVICE_NAME="hsirb-system"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
APP_PATH="/var/www/html/hsirb"
SOCKET_PATH="${APP_PATH}/hsirb-system.sock"
VENV_PATH="/home/ccastille/hsirb-system/venv"
APP_DIR="/home/ccastille/hsirb-system"

# ============================================================================
# COLORS
# ============================================================================
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🔧 Setting up Gunicorn service: ${SERVICE_NAME}${NC}\n"

# ============================================================================
# CREATE SYSTEMD SERVICE FILE
# ============================================================================
echo -e "${YELLOW}📝 Creating systemd service file...${NC}"
ssh bayoupal << EOF
    echo "nsutemppasswd123" | sudo -S tee ${SERVICE_FILE} > /dev/null << 'SERVICE_CONFIG'
[Unit]
Description=HSIRB Study Management System Gunicorn daemon
After=network.target postgresql.service

[Service]
User=apache
Group=apache
WorkingDirectory=${APP_DIR}
Environment="PATH=${VENV_PATH}/bin"
EnvironmentFile=${APP_DIR}/.env
ExecStart=${VENV_PATH}/bin/gunicorn \\
    --workers 3 \\
    --bind unix:${SOCKET_PATH} \\
    --timeout 120 \\
    --access-logfile /var/log/hsirb/access.log \\
    --error-logfile /var/log/hsirb/error.log \\
    config.wsgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE_CONFIG

    # Create log directory
    echo "nsutemppasswd123" | sudo -S mkdir -p /var/log/hsirb
    echo "nsutemppasswd123" | sudo -S chown apache:apache /var/log/hsirb
    
    # Set socket directory permissions
    echo "nsutemppasswd123" | sudo -S mkdir -p ${APP_PATH}
    echo "nsutemppasswd123" | sudo -S chown apache:apache ${APP_PATH}
    
    # Reload systemd
    echo "nsutemppasswd123" | sudo -S systemctl daemon-reload
    
    # Enable service
    echo "nsutemppasswd123" | sudo -S systemctl enable ${SERVICE_NAME}
    
    echo "✅ Service file created and enabled!"
EOF

echo -e "\n${GREEN}✅ Gunicorn service setup complete!${NC}"
echo -e "${YELLOW}📝 Service commands:${NC}"
echo -e "   Start:   ssh bayoupal 'echo \"nsutemppasswd123\" | sudo -S systemctl start ${SERVICE_NAME}'"
echo -e "   Stop:    ssh bayoupal 'echo \"nsutemppasswd123\" | sudo -S systemctl stop ${SERVICE_NAME}'"
echo -e "   Restart: ssh bayoupal 'echo \"nsutemppasswd123\" | sudo -S systemctl restart ${SERVICE_NAME}'"
echo -e "   Status:  ssh bayoupal 'sudo systemctl status ${SERVICE_NAME}'"
echo -e "   Logs:    ssh bayoupal 'sudo journalctl -u ${SERVICE_NAME} -f'"
