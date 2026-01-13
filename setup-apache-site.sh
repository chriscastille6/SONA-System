#!/bin/bash
# File location: setup-apache-site.sh
# What this file does: Sets up Apache configuration for HSIRB Study Management System
# This configures Apache to proxy to Gunicorn (RHEL version)

# ============================================================================
# CONFIGURATION
# ============================================================================
SITE_NAME="hsirb"
SITE_PATH="/var/www/html/${SITE_NAME}"
CONFIG_FILE="/etc/httpd/conf.d/${SITE_NAME}.conf"
SOCKET_PATH="/var/www/html/${SITE_NAME}/hsirb-system.sock"

# ============================================================================
# COLORS
# ============================================================================
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🔧 Setting up Apache site: ${SITE_NAME}${NC}\n"

# ============================================================================
# CREATE WEB DIRECTORY
# ============================================================================
echo -e "${YELLOW}📁 Creating web directory...${NC}"
ssh bayoupal << EOF
    echo "nsutemppasswd123" | sudo -S mkdir -p ${SITE_PATH}
    echo "nsutemppasswd123" | sudo -S mkdir -p ${SITE_PATH}/static
    echo "nsutemppasswd123" | sudo -S mkdir -p ${SITE_PATH}/media
    echo "nsutemppasswd123" | sudo -S chown -R apache:apache ${SITE_PATH}
    echo "nsutemppasswd123" | sudo -S chmod -R 755 ${SITE_PATH}
EOF

# ============================================================================
# CREATE APACHE CONFIG (Proxy to Gunicorn) - RHEL Version
# ============================================================================
echo -e "${YELLOW}⚙️  Creating Apache configuration...${NC}"
ssh bayoupal << EOF
    echo "nsutemppasswd123" | sudo -S tee ${CONFIG_FILE} > /dev/null << 'APACHE_CONFIG'
# HSIRB Study Management System - Apache Configuration
# Proxy to Gunicorn via Unix socket

# Load required modules (if not already loaded in main config)
LoadModule proxy_module modules/mod_proxy.so
LoadModule proxy_http_module modules/mod_proxy_http.so
LoadModule ssl_module modules/mod_ssl.so
LoadModule rewrite_module modules/mod_rewrite.so

<VirtualHost *:443>
    ServerName bayoupal.nicholls.edu
    
    # SSL Configuration
    SSLEngine on
    SSLCertificateFile /etc/ssl/certs/platform.crt
    SSLCertificateKeyFile /etc/ssl/private/platform.key
    
    # Proxy to Gunicorn
    ProxyPreserveHost On
    ProxyPass /${SITE_NAME}/static/ !
    ProxyPass /${SITE_NAME}/media/ !
    ProxyPass /${SITE_NAME}/ http://unix:${SOCKET_PATH}/
    ProxyPassReverse /${SITE_NAME}/ http://unix:${SOCKET_PATH}/
    
    # Static files
    Alias /${SITE_NAME}/static ${SITE_PATH}/static
    <Directory ${SITE_PATH}/static>
        Options -Indexes
        Require all granted
    </Directory>
    
    # Media files
    Alias /${SITE_NAME}/media ${SITE_PATH}/media
    <Directory ${SITE_PATH}/media>
        Options -Indexes
        Require all granted
    </Directory>
    
    # Logs
    ErrorLog /var/log/httpd/${SITE_NAME}_error.log
    CustomLog /var/log/httpd/${SITE_NAME}_access.log combined
</VirtualHost>

# HTTP to HTTPS redirect
<VirtualHost *:80>
    ServerName bayoupal.nicholls.edu
    Redirect permanent /${SITE_NAME} https://bayoupal.nicholls.edu/${SITE_NAME}/
</VirtualHost>
APACHE_CONFIG
EOF

# ============================================================================
# TEST AND RESTART
# ============================================================================
echo -e "${YELLOW}🧪 Testing Apache configuration...${NC}"
ssh bayoupal "echo 'nsutemppasswd123' | sudo -S httpd -t"

if [ $? -eq 0 ]; then
    echo -e "${YELLOW}🚀 Restarting Apache...${NC}"
    ssh bayoupal "echo 'nsutemppasswd123' | sudo -S systemctl restart httpd"
    
    echo -e "\n${GREEN}✅ Apache site setup complete!${NC}"
    echo -e "${YELLOW}🌐 Your site will be available at:${NC}"
    echo -e "   https://bayoupal.nicholls.edu/${SITE_NAME}/"
    echo -e "\n${YELLOW}📝 Next steps:${NC}"
    echo -e "   1. Set up PostgreSQL: ./setup-postgresql.sh"
    echo -e "   2. Set up Gunicorn service: ./setup-gunicorn-service.sh"
    echo -e "   3. Configure .env file on server"
    echo -e "   4. Deploy: ./deploy-to-server.sh"
else
    echo -e "\n${RED}❌ Apache configuration test failed!${NC}"
    exit 1
fi
