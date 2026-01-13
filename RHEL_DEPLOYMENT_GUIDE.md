# 🔴 Red Hat Enterprise Linux 10 Deployment Guide

Complete guide for deploying SONA System on RHEL 10 campus virtual machine.

---

## 📋 Prerequisites

- ✅ RHEL 10 virtual machine
- ✅ SSH access to server
- ✅ sudo/root access
- ✅ Network access (ports 80/443)
- ✅ Domain name or IP address

---

## 🔧 Step 1: Initial Server Setup

### Connect to Server

```bash
ssh username@your-server-ip
```

### Update System

```bash
sudo dnf update -y
```

### Install EPEL Repository (Required for some packages)

```bash
sudo dnf install epel-release -y
```

---

## 📦 Step 2: Install Required Software

### Install Python and Development Tools

```bash
# Python 3.11+ and pip
sudo dnf install python3 python3-pip python3-devel -y

# Development tools (for compiling Python packages)
sudo dnf groupinstall "Development Tools" -y

# Additional build dependencies
sudo dnf install gcc gcc-c++ make -y
```

### Install PostgreSQL

```bash
# Install PostgreSQL server and client
sudo dnf install postgresql15-server postgresql15-contrib -y

# Initialize database
sudo postgresql-setup --initdb

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Install Nginx

```bash
# Install Nginx
sudo dnf install nginx -y

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### Install Git

```bash
sudo dnf install git -y
```

### Install Additional Dependencies

```bash
# PostgreSQL development libraries
sudo dnf install postgresql15-devel -y

# Other useful tools
sudo dnf install wget curl -y
```

---

## 🗄️ Step 3: Configure PostgreSQL

### Configure PostgreSQL Authentication

```bash
# Edit PostgreSQL configuration
sudo nano /var/lib/pgsql/data/pg_hba.conf
```

**Find and update these lines** (change `ident` to `md5` for password auth):

```
# IPv4 local connections:
host    all             all             127.0.0.1/32            md5

# IPv6 local connections:
host    all             all             ::1/128                 md5
```

**Restart PostgreSQL:**
```bash
sudo systemctl restart postgresql
```

### Create Database and User

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL prompt:
CREATE DATABASE sona_db;
CREATE USER sona_user WITH PASSWORD 'your-secure-password-here';
ALTER ROLE sona_user SET client_encoding TO 'utf8';
ALTER ROLE sona_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE sona_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE sona_db TO sona_user;
\q
```

### Test Connection

```bash
psql -U sona_user -d sona_db -h localhost
# Enter password when prompted
# Type \q to exit
```

---

## 📦 Step 4: Deploy Application

### Create Application Directory

```bash
# Create directory for app
sudo mkdir -p /var/www/sona-system
sudo chown $USER:$USER /var/www/sona-system
cd /var/www/sona-system
```

### Clone Repository

```bash
# Clone from GitHub
git clone https://github.com/chriscastille6/SONA-System.git .

# Or if you have SSH access:
# git clone git@github.com:chriscastille6/SONA-System.git .
```

### Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** If you encounter compilation errors, you may need:
```bash
sudo dnf install python3-devel postgresql15-devel -y
```

---

## ⚙️ Step 5: Configure Application

### Create Environment File

```bash
cd /var/www/sona-system
nano .env
```

**Add these variables:**

```bash
# Django Settings
SECRET_KEY=your-super-secret-key-here-generate-with-openssl-rand-hex-32
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-server-ip

# Database
DATABASE_URL=postgresql://sona_user:your-secure-password-here@localhost:5432/sona_db

# Site Configuration
SITE_NAME=Research Participant System
INSTITUTION_NAME=Nicholls State University
SITE_URL=https://your-domain.com

# Email (configure with your university SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.nicholls.edu
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@nicholls.edu
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@nicholls.edu

# Celery (if using Redis - install separately)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

**Generate SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### Run Migrations

```bash
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

---

## 🌐 Step 6: Configure Gunicorn

### Create Gunicorn Service File

```bash
sudo nano /etc/systemd/system/sona-system.service
```

**Add this content:**

```ini
[Unit]
Description=SONA System Gunicorn daemon
After=network.target postgresql.service

[Service]
User=apache
Group=apache
WorkingDirectory=/var/www/sona-system
Environment="PATH=/var/www/sona-system/venv/bin"
ExecStart=/var/www/sona-system/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/var/www/sona-system/sona-system.sock \
    --timeout 120 \
    config.wsgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Note:** On RHEL, you might use `apache` user/group or create a dedicated user:
```bash
# Create dedicated user (optional)
sudo useradd -r -s /bin/false sona-user
sudo chown -R sona-user:sona-user /var/www/sona-system
```

### Set Permissions

```bash
sudo chown -R apache:apache /var/www/sona-system
sudo chmod -R 755 /var/www/sona-system
```

### Start and Enable Service

```bash
sudo systemctl daemon-reload
sudo systemctl start sona-system
sudo systemctl enable sona-system
sudo systemctl status sona-system
```

---

## 🔒 Step 7: Configure SELinux (Important for RHEL)

RHEL has SELinux enabled by default. Configure it for your application:

### Allow Nginx to Connect to Socket

```bash
# Allow Nginx to connect to the socket
sudo setsebool -P httpd_can_network_connect 1

# Allow Nginx to read files
sudo setsebool -P httpd_read_user_content 1

# Set proper context for application directory
sudo semanage fcontext -a -t httpd_sys_content_t "/var/www/sona-system(/.*)?"
sudo restorecon -Rv /var/www/sona-system
```

### If SELinux Blocks Something

```bash
# Check SELinux denials
sudo ausearch -m avc -ts recent

# Temporarily set SELinux to permissive (for testing)
sudo setenforce 0

# Permanently (not recommended for production)
# Edit /etc/selinux/config and set SELINUX=permissive
```

---

## 🌐 Step 8: Configure Nginx

### Create Nginx Configuration

```bash
sudo nano /etc/nginx/conf.d/sona-system.conf
```

**Add this content:**

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Redirect HTTP to HTTPS (if you have SSL)
    # return 301 https://$server_name$request_uri;

    # Or for HTTP only (development):
    location / {
        proxy_pass http://unix:/var/www/sona-system/sona-system.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    location /static/ {
        alias /var/www/sona-system/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/sona-system/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

### Test and Reload Nginx

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔐 Step 9: Configure Firewall (firewalld)

RHEL uses `firewalld` instead of `ufw`:

```bash
# Allow HTTP
sudo firewall-cmd --permanent --add-service=http

# Allow HTTPS
sudo firewall-cmd --permanent --add-service=https

# Allow SSH (if not already allowed)
sudo firewall-cmd --permanent --add-service=ssh

# Reload firewall
sudo firewall-cmd --reload

# Check status
sudo firewall-cmd --list-all
```

---

## 🔒 Step 10: Set Up SSL (Optional but Recommended)

### Using Let's Encrypt (Free SSL)

```bash
# Install Certbot
sudo dnf install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

Certbot will automatically configure Nginx for HTTPS.

---

## 🔄 Step 11: Set Up Auto-Deploy Script

### Create Deploy Script

```bash
nano /var/www/sona-system/deploy.sh
```

**Add this content:**

```bash
#!/bin/bash
set -e

cd /var/www/sona-system
source venv/bin/activate

echo "Pulling latest changes..."
git pull origin main

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Restarting service..."
sudo systemctl restart sona-system

echo "Deployment complete!"
```

**Make executable:**
```bash
chmod +x /var/www/sona-system/deploy.sh
```

**Allow sudo without password for this script (optional):**
```bash
# Edit sudoers (use visudo for safety)
sudo visudo

# Add this line (replace 'username' with your user):
username ALL=(ALL) NOPASSWD: /bin/systemctl restart sona-system
```

---

## 📊 Step 12: Set Up Logging and Monitoring

### View Application Logs

```bash
# View service logs
sudo journalctl -u sona-system -f

# View recent logs
sudo journalctl -u sona-system -n 100

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Set Up Log Rotation (Optional)

```bash
sudo nano /etc/logrotate.d/sona-system
```

**Add:**
```
/var/www/sona-system/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 apache apache
    sharedscripts
}
```

---

## ✅ Step 13: Test Deployment

1. **Check services are running:**
   ```bash
   sudo systemctl status sona-system
   sudo systemctl status nginx
   sudo systemctl status postgresql
   ```

2. **Test from command line:**
   ```bash
   curl http://localhost
   ```

3. **Visit in browser:** `http://your-domain.com` (or IP address)

4. **Check admin panel:** `http://your-domain.com/admin`

---

## 🔄 Step 14: Updating the Application

### Manual Update

```bash
cd /var/www/sona-system
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
sudo systemctl restart sona-system
```

### Or Use Deploy Script

```bash
/var/www/sona-system/deploy.sh
```

---

## 🐛 Troubleshooting

### Application Not Starting?

```bash
# Check service status
sudo systemctl status sona-system

# Check logs
sudo journalctl -u sona-system -n 100

# Check if socket file exists and permissions
ls -la /var/www/sona-system/sona-system.sock
sudo chown apache:apache /var/www/sona-system/sona-system.sock
```

### SELinux Issues?

```bash
# Check SELinux denials
sudo ausearch -m avc -ts recent

# Temporarily disable for testing
sudo setenforce 0

# Check current mode
getenforce
```

### Nginx Errors?

```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log

# Check SELinux context
ls -Z /var/www/sona-system/sona-system.sock
```

### Database Connection Issues?

```bash
# Test PostgreSQL connection
psql -U sona_user -d sona_db -h localhost

# Check PostgreSQL is running
sudo systemctl status postgresql

# Check PostgreSQL logs
sudo tail -f /var/lib/pgsql/data/log/postgresql-*.log
```

### Permission Issues?

```bash
# Fix ownership
sudo chown -R apache:apache /var/www/sona-system
sudo chmod -R 755 /var/www/sona-system

# Fix SELinux context
sudo restorecon -Rv /var/www/sona-system
```

### Python Package Installation Issues?

```bash
# Install development tools
sudo dnf groupinstall "Development Tools" -y
sudo dnf install python3-devel postgresql15-devel -y

# Try installing again
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🔒 Security Best Practices for RHEL

1. ✅ **Keep system updated:**
   ```bash
   sudo dnf update -y
   ```

2. ✅ **Configure SELinux properly** (don't just disable it)

3. ✅ **Use strong passwords** for database and Django SECRET_KEY

4. ✅ **Configure firewall:** `firewall-cmd`

5. ✅ **Use HTTPS:** Set up SSL certificate

6. ✅ **Regular backups:** Set up automated database backups

7. ✅ **Monitor logs:** Check for suspicious activity

8. ✅ **Limit SSH access:** Use key-based authentication

9. ✅ **Keep Django updated:** `pip install --upgrade Django`

10. ✅ **Review SELinux policies** regularly

---

## 📋 Quick Reference Commands

```bash
# Service management
sudo systemctl start sona-system
sudo systemctl stop sona-system
sudo systemctl restart sona-system
sudo systemctl status sona-system

# View logs
sudo journalctl -u sona-system -f

# Firewall
sudo firewall-cmd --list-all
sudo firewall-cmd --reload

# SELinux
getenforce
sudo setenforce 0  # Permissive (testing)
sudo setenforce 1  # Enforcing (production)

# Database
sudo systemctl status postgresql
sudo -u postgres psql

# Nginx
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🎯 Next Steps

Once deployed, you can:
1. ✅ Access the application via browser
2. ✅ Set up regular backups
3. ✅ Configure email notifications
4. ✅ Set up monitoring/alerting
5. ✅ Create user accounts for your team

---

**Your SONA system is now ready for RHEL 10 deployment!** 🔴

If you provide SSH access, I can help you execute these steps directly on the server.
