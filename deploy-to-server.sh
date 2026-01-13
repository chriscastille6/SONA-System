#!/bin/bash
# File location: deploy-to-server.sh
# What this file does: Deploys HSIRB Study Management System to bayoupal.nicholls.edu
# This script pulls from GitHub and sets up the Django application

# ============================================================================
# CONFIGURATION
# ============================================================================
SERVER_USER="ccastille"
SERVER_HOST="bayoupal.nicholls.edu"
REMOTE_PATH="~/hsirb-system"
WEB_PATH="/var/www/html/hsirb"
GITHUB_REPO="https://github.com/chriscastille6/SONA-System.git"
GITHUB_BRANCH="main"

# ============================================================================
# COLORS
# ============================================================================
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Deploying HSIRB Study Management System to ${SERVER_HOST}...${NC}\n"

# ============================================================================
# DEPLOY TO SERVER
# ============================================================================
echo -e "${BLUE}📦 Step 1: Cloning/updating repository on server...${NC}"
ssh bayoupal << 'DEPLOY_SCRIPT'
    # Create directory if it doesn't exist
    mkdir -p ~/hsirb-system
    
    # If directory exists but no .git, remove and clone fresh
    if [ -d ~/hsirb-system ] && [ ! -d ~/hsirb-system/.git ]; then
        echo "Directory exists but not a git repo. Removing and cloning fresh..."
        rm -rf ~/hsirb-system
    fi
    
    cd ~/hsirb-system
    
    # Clone if doesn't exist, otherwise pull
    if [ ! -d ".git" ]; then
        echo "Cloning repository..."
        git clone https://github.com/chriscastille6/SONA-System.git ~/hsirb-system
        cd ~/hsirb-system
    else
        echo "Pulling latest changes..."
        git pull origin main
    fi
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate venv and install/update dependencies
    echo "Installing dependencies..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Run migrations
    echo "Running database migrations..."
    python manage.py migrate --noinput
    
    # Collect static files
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
    
    # Copy static files to web directory
    echo "Copying static files to web directory..."
    echo "nsutemppasswd123" | sudo -S mkdir -p /var/www/html/hsirb/static
    echo "nsutemppasswd123" | sudo -S cp -r staticfiles/* /var/www/html/hsirb/static/
    echo "nsutemppasswd123" | sudo -S chown -R apache:apache /var/www/html/hsirb/static
    
    # Restart Gunicorn service
    echo "Restarting Gunicorn service..."
    echo "nsutemppasswd123" | sudo -S systemctl restart hsirb-system || echo "Service not running yet (first deployment)"
    
    echo "✅ Deployment complete on server!"
DEPLOY_SCRIPT

if [ $? -ne 0 ]; then
    echo -e "\n${RED}❌ Deployment failed!${NC}"
    exit 1
fi

echo -e "\n${GREEN}✅ Deployment successful!${NC}"
echo -e "${YELLOW}📝 Next steps:${NC}"
echo -e "   1. SSH to server: ssh bayoupal"
echo -e "   2. Set up .env file: cd ~/hsirb-system && cp env.template .env && nano .env"
echo -e "   3. Run initial setup: ./setup-postgresql.sh (if not done)"
echo -e "   4. Create superuser: source venv/bin/activate && python manage.py createsuperuser"
echo -e "   5. Restart service: echo 'nsutemppasswd123' | sudo -S systemctl restart hsirb-system"
echo -e "   6. Test site: https://bayoupal.nicholls.edu/hsirb/"
