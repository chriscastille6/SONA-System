#!/bin/bash
# RHEL 10 Setup Script for SONA System
# Run this script with sudo privileges

set -e

echo "=========================================="
echo "SONA System - RHEL 10 Setup Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root or with sudo${NC}"
    exit 1
fi

echo -e "${GREEN}Step 1: Updating system...${NC}"
dnf update -y

echo -e "${GREEN}Step 2: Installing EPEL repository...${NC}"
dnf install epel-release -y

echo -e "${GREEN}Step 3: Installing Python and development tools...${NC}"
dnf install python3 python3-pip python3-devel -y
dnf groupinstall "Development Tools" -y
dnf install gcc gcc-c++ make -y

echo -e "${GREEN}Step 4: Installing PostgreSQL...${NC}"
dnf install postgresql15-server postgresql15-contrib postgresql15-devel -y
postgresql-setup --initdb
systemctl start postgresql
systemctl enable postgresql

echo -e "${GREEN}Step 5: Installing Nginx...${NC}"
dnf install nginx -y
systemctl start nginx
systemctl enable nginx

echo -e "${GREEN}Step 6: Installing Git and utilities...${NC}"
dnf install git wget curl -y

echo -e "${GREEN}Step 7: Configuring firewall...${NC}"
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --permanent --add-service=ssh
firewall-cmd --reload

echo -e "${GREEN}Step 8: Creating application directory...${NC}"
mkdir -p /var/www/sona-system
chown $SUDO_USER:$SUDO_USER /var/www/sona-system

echo -e "${GREEN}=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Configure PostgreSQL (see RHEL_DEPLOYMENT_GUIDE.md)"
echo "2. Clone your repository to /var/www/sona-system"
echo "3. Set up virtual environment and install dependencies"
echo "4. Configure .env file"
echo "5. Run migrations"
echo "6. Set up Gunicorn service"
echo "7. Configure Nginx"
echo "8. Configure SELinux"
echo ""
echo -e "${GREEN}See RHEL_DEPLOYMENT_GUIDE.md for detailed instructions${NC}"
