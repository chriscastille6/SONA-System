# 🏫 Campus Linux Server Deployment Guide

Complete guide for deploying SONA System on your university's Linux server.

---

## 📋 Prerequisites

- ✅ Linux server (Ubuntu 20.04+ or similar)
- ✅ SSH access to server
- ✅ sudo/root access (for initial setup)
- ✅ Domain name or IP address
- ✅ Port 80/443 open (for web traffic)

---

## 🔧 Step 1: Server Setup

### Connect to Server

```bash
ssh username@your-server-ip
```

### Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### Install Required Software

```bash
# Python and pip
sudo apt install python3 python3-pip python3-venv -y

# PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Nginx (web server)
sudo apt install nginx -y

# Git
sudo apt install git -y

# Build tools (for some Python packages)
sudo apt install build-essential libpq-dev -y
```

---

## 🗄️ Step 2: Set Up PostgreSQL Database

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

## 📦 Step 3: Deploy Application

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

---

## ⚙️ Step 4: Configure Application

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

# Celery (if using Redis)
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

## 🌐 Step 5: Configure Gunicorn

### Create Gunicorn Service File

```bash
sudo nano /etc/systemd/system/sona-system.service
```

**Add this content:**

```ini
[Unit]
Description=SONA System Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/sona-system
Environment="PATH=/var/www/sona-system/venv/bin"
ExecStart=/var/www/sona-system/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/var/www/sona-system/sona-system.sock \
    --timeout 120 \
    config.wsgi:application

[Install]
WantedBy=multi-user.target
```

**Note:** Replace `www-data` with your user if needed, or create a dedicated user.

### Start and Enable Service

```bash
sudo systemctl daemon-reload
sudo systemctl start sona-system
sudo systemctl enable sona-system
sudo systemctl status sona-system
```

---

## 🔒 Step 6: Configure Nginx

### Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/sona-system
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
    }

    location /static/ {
        alias /var/www/sona-system/staticfiles/;
    }

    location /media/ {
        alias /var/www/sona-system/media/;
    }
}
```

### Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/sona-system /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

---

## 🔐 Step 7: Set Up SSL (Optional but Recommended)

### Using Let's Encrypt (Free SSL)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

Certbot will automatically:
- ✅ Get SSL certificate
- ✅ Configure Nginx for HTTPS
- ✅ Set up auto-renewal

---

## 🔄 Step 8: Set Up Auto-Deploy (Optional)

### Create Deploy Script

```bash
nano /var/www/sona-system/deploy.sh
```

**Add this content:**

```bash
#!/bin/bash
cd /var/www/sona-system
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
sudo systemctl restart sona-system
echo "Deployment complete!"
```

**Make executable:**
```bash
chmod +x /var/www/sona-system/deploy.sh
```

### Set Up Git Webhook (Optional)

For automatic deployment on `git push`, set up a webhook or use a simple cron job.

---

## 📊 Step 9: Set Up Monitoring (Optional)

### Install and Configure Logging

```bash
# View application logs
sudo journalctl -u sona-system -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 🔧 Step 10: Firewall Configuration

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
sudo ufw status
```

---

## ✅ Step 11: Test Deployment

1. **Visit your domain:** `http://your-domain.com` (or `https://` if SSL configured)
2. **Check admin panel:** `http://your-domain.com/admin`
3. **Test user registration**
4. **Check logs** if issues: `sudo journalctl -u sona-system -n 50`

---

## 🔄 Updating the Application

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

# Check if socket file exists
ls -la /var/www/sona-system/sona-system.sock
```

### Nginx Errors?

```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log

# Check if Gunicorn is running
sudo systemctl status sona-system
```

### Database Connection Issues?

```bash
# Test PostgreSQL connection
psql -U sona_user -d sona_db -h localhost

# Check PostgreSQL is running
sudo systemctl status postgresql
```

### Permission Issues?

```bash
# Fix ownership
sudo chown -R www-data:www-data /var/www/sona-system
sudo chmod -R 755 /var/www/sona-system
```

---

## 📋 Maintenance Checklist

**Daily:**
- [ ] Check application logs
- [ ] Monitor disk space
- [ ] Check database backups

**Weekly:**
- [ ] Update system packages: `sudo apt update && sudo apt upgrade`
- [ ] Review error logs
- [ ] Check SSL certificate (if using Let's Encrypt)

**Monthly:**
- [ ] Review security updates
- [ ] Backup database
- [ ] Review application performance

---

## 🔒 Security Best Practices

1. ✅ **Keep system updated:** `sudo apt update && sudo apt upgrade`
2. ✅ **Use strong passwords** for database and Django SECRET_KEY
3. ✅ **Enable firewall:** `sudo ufw enable`
4. ✅ **Use HTTPS:** Set up SSL certificate
5. ✅ **Regular backups:** Set up automated database backups
6. ✅ **Monitor logs:** Check for suspicious activity
7. ✅ **Limit SSH access:** Use key-based authentication
8. ✅ **Keep Django updated:** `pip install --upgrade Django`

---

## 📞 Need Help?

Common issues and solutions are in the troubleshooting section above. For Django-specific issues, check:
- Django logs: `sudo journalctl -u sona-system`
- Nginx logs: `/var/log/nginx/error.log`
- Application logs: Check your Django `LOGGING` configuration

---

**Your SONA system is now running on your campus server!** 🎉
