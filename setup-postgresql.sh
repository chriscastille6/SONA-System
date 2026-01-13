#!/bin/bash
# File location: setup-postgresql.sh
# What this file does: Sets up PostgreSQL database for HSIRB System

# ============================================================================
# CONFIGURATION
# ============================================================================
DB_NAME="hsirb_db"
DB_USER="hsirb_user"
# Generate a secure password (you'll be prompted to save it)
DB_PASSWORD=$(openssl rand -base64 32)

# ============================================================================
# COLORS
# ============================================================================
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}🗄️  Setting up PostgreSQL database for HSIRB System${NC}\n"

# ============================================================================
# CHECK POSTGRESQL
# ============================================================================
echo -e "${BLUE}📋 Checking PostgreSQL installation...${NC}"
ssh bayoupal << 'CHECK_POSTGRES'
    if ! command -v psql &> /dev/null; then
        echo "PostgreSQL not found. Installing..."
        echo "nsutemppasswd123" | sudo -S dnf install postgresql15-server postgresql15-contrib -y
        echo "nsutemppasswd123" | sudo -S postgresql-setup --initdb
        echo "nsutemppasswd123" | sudo -S systemctl start postgresql
        echo "nsutemppasswd123" | sudo -S systemctl enable postgresql
    else
        echo "PostgreSQL is installed."
        psql --version
    fi
    
    # Ensure PostgreSQL is running
    echo "nsutemppasswd123" | sudo -S systemctl start postgresql
CHECK_POSTGRES

# ============================================================================
# CREATE DATABASE AND USER
# ============================================================================
echo -e "${BLUE}📦 Creating database and user...${NC}"
echo -e "${YELLOW}⚠️  Generated password: ${DB_PASSWORD}${NC}"
echo -e "${YELLOW}⚠️  SAVE THIS PASSWORD - you'll need it for .env file!${NC}\n"

# Create SQL script and execute it
ssh bayoupal << EOF
    cat > /tmp/setup_hsirb_db.sql << SQLSCRIPT
-- Create database
CREATE DATABASE ${DB_NAME};

-- Create user
CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';

-- Set permissions
ALTER ROLE ${DB_USER} SET client_encoding TO 'utf8';
ALTER ROLE ${DB_USER} SET default_transaction_isolation TO 'read committed';
ALTER ROLE ${DB_USER} SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
SQLSCRIPT

    # Execute as postgres user
    echo "nsutemppasswd123" | sudo -S -u postgres psql -f /tmp/setup_hsirb_db.sql
    
    # Grant schema permissions
    echo "nsutemppasswd123" | sudo -S -u postgres psql -d ${DB_NAME} << SCHEMA_SCRIPT
GRANT ALL ON SCHEMA public TO ${DB_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${DB_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${DB_USER};
SCHEMA_SCRIPT
    
    # Clean up
    rm /tmp/setup_hsirb_db.sql
EOF

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Database setup complete!${NC}"
    echo -e "${YELLOW}📝 Database credentials:${NC}"
    echo -e "   Database: ${DB_NAME}"
    echo -e "   User: ${DB_USER}"
    echo -e "   Password: ${DB_PASSWORD}"
    echo -e "\n${YELLOW}⚠️  Add this to your .env file on the server:${NC}"
    echo -e "   DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}"
    echo -e "\n${YELLOW}💾 Saving password to ~/hsirb-db-password.txt on server...${NC}"
    ssh bayoupal "echo '${DB_PASSWORD}' > ~/hsirb-db-password.txt && chmod 600 ~/hsirb-db-password.txt"
    echo -e "${GREEN}✅ Password saved securely on server${NC}"
else
    echo -e "\n${RED}❌ Database setup failed!${NC}"
    exit 1
fi
