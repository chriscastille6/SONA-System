#!/bin/bash
# Fix Apache CSRF Headers for HSIRB System
# This script adds the necessary proxy headers to Apache for CSRF verification
# Usage: SUDO_PASSWORD=yourpassword bash fix-apache-csrf.sh

# ============================================================================
# CONFIGURATION
# ============================================================================
CONFIG_FILE="/etc/httpd/conf.d/hsirb.conf"
MAIN_CONFIG="/etc/httpd/conf/httpd.conf"
SUDO_PASSWORD="${SUDO_PASSWORD:-nsutemppasswd123}"

# ============================================================================
# COLORS
# ============================================================================
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔧 Fixing Apache CSRF Headers...${NC}\n"

# ============================================================================
# ENABLE HEADERS MODULE
# ============================================================================
echo -e "${YELLOW}📦 Enabling headers module...${NC}"
if ! grep -q "^LoadModule headers_module" "$MAIN_CONFIG"; then
    if grep -q "^#LoadModule headers_module" "$MAIN_CONFIG"; then
        echo "$SUDO_PASSWORD" | sudo -S sed -i 's/^#LoadModule headers_module/LoadModule headers_module/' "$MAIN_CONFIG"
        echo -e "${GREEN}✅ Headers module enabled${NC}"
    else
        echo "LoadModule headers_module modules/mod_headers.so" | echo "$SUDO_PASSWORD" | sudo -S tee -a "$MAIN_CONFIG" > /dev/null
        echo -e "${GREEN}✅ Headers module added${NC}"
    fi
else
    echo -e "${GREEN}✅ Headers module already enabled${NC}"
fi

# ============================================================================
# ADD PROXY HEADERS TO APACHE CONFIG
# ============================================================================
echo -e "${YELLOW}⚙️  Adding proxy headers to Apache config...${NC}"

# Check if headers are already present
if grep -q "X-Forwarded-Proto" "$CONFIG_FILE"; then
    echo -e "${GREEN}✅ Proxy headers already present${NC}"
else
    # Create backup
    echo "$SUDO_PASSWORD" | sudo -S cp "$CONFIG_FILE" "${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Add headers before the ProxyPreserveHost line
    echo "$SUDO_PASSWORD" | sudo -S sed -i '/# Proxy to Gunicorn/i\    # Proxy headers for CSRF and SSL\n    RequestHeader set X-Forwarded-Proto "https"\n    RequestHeader set X-Forwarded-Port "443"\n' "$CONFIG_FILE"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Proxy headers added${NC}"
    else
        echo -e "${RED}❌ Failed to add headers${NC}"
        exit 1
    fi
fi

# ============================================================================
# TEST AND RESTART APACHE
# ============================================================================
echo -e "${YELLOW}🧪 Testing Apache configuration...${NC}"
if echo "$SUDO_PASSWORD" | sudo -S httpd -t; then
    echo -e "${GREEN}✅ Apache configuration is valid${NC}"
    
    echo -e "${YELLOW}🚀 Restarting Apache...${NC}"
    echo "$SUDO_PASSWORD" | sudo -S systemctl restart httpd
    
    if [ $? -eq 0 ]; then
        echo -e "\n${GREEN}✅ Apache CSRF headers fix complete!${NC}"
        echo -e "${YELLOW}📝 The following headers were added:${NC}"
        echo -e "   - X-Forwarded-Proto: https"
        echo -e "   - X-Forwarded-Port: 443"
        echo -e "\n${GREEN}✅ You can now try creating an account again!${NC}"
    else
        echo -e "${RED}❌ Failed to restart Apache${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Apache configuration test failed!${NC}"
    echo -e "${YELLOW}⚠️  Restoring backup...${NC}"
    echo "$SUDO_PASSWORD" | sudo -S cp "${CONFIG_FILE}.backup."* "$CONFIG_FILE" 2>/dev/null
    exit 1
fi
