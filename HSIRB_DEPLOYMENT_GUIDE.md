# 🏫 HSIRB Study Management System - Server Deployment Guide

Complete guide for deploying the HSIRB Study Management System to bayoupal.nicholls.edu

## 📋 Prerequisites

- ✅ SSH access to bayoupal.nicholls.edu (`ssh bayoupal`)
- ✅ Sudo password: `nsutemppasswd123`
- ✅ PostgreSQL (will be installed if needed)
- ✅ Python 3 (will be installed if needed)
- ✅ Git installed on server

## 🚀 Quick Start Deployment

### Step 1: Set Up PostgreSQL Database

```bash
chmod +x setup-postgresql.sh
./setup-postgresql.sh
```

**Important:** Save the database password that's displayed! It's also saved to `~/hsirb-db-password.txt` on the server.

### Step 2: Set Up Apache Configuration

```bash
chmod +x setup-apache-site.sh
./setup-apache-site.sh
```

This creates the Apache virtual host configuration to proxy to Gunicorn.

### Step 3: Set Up Gunicorn Service

```bash
chmod +x setup-gunicorn-service.sh
./setup-gunicorn-service.sh
```

This creates the systemd service file for running Gunicorn.

### Step 4: Deploy Application

```bash
chmod +x deploy-to-server.sh
./deploy-to-server.sh
```

This will:
- Clone the repository from GitHub
- Set up virtual environment
- Install dependencies
- Run migrations
- Collect static files

### Step 5: Configure Environment Variables

SSH to the server and create the .env file:

```bash
ssh bayoupal
cd ~/hsirb-system
cp env.template .env
nano .env
```

**Required changes:**
1. **Generate SECRET_KEY:**
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(50))"
   ```
   Copy the output and paste as `SECRET_KEY` value

2. **Add DATABASE_URL:**
   - Get password from: `cat ~/hsirb-db-password.txt`
   - Format: `postgresql://hsirb_user:PASSWORD@localhost:5432/hsirb_db`

3. **Update email settings** with your Nicholls email credentials

4. **Verify ALLOWED_HOSTS** includes `bayoupal.nicholls.edu`

### Step 6: Initialize Database (First Time Only)

```bash
ssh bayoupal
cd ~/hsirb-system
source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
```

Follow prompts to create admin user.

### Step 7: Start Services

```bash
# Start Gunicorn service
ssh bayoupal 'echo "nsutemppasswd123" | sudo -S systemctl start hsirb-system'

# Restart Apache (to pick up new config)
ssh bayoupal 'echo "nsutemppasswd123" | sudo -S systemctl restart httpd'

# Check status
ssh bayoupal 'sudo systemctl status hsirb-system'
```

### Step 8: Test

Visit: **https://bayoupal.nicholls.edu/hsirb/**

You should see the HSIRB Study Management System homepage!

## 📝 File Structure on Server

```
~/hsirb-system/              # Application directory (user space)
├── .env                    # Environment variables (create from template)
├── .git/                   # Git repository
├── venv/                   # Virtual environment
├── staticfiles/            # Collected static files
├── media/                  # User uploads (if any)
└── ...                     # Django application files

/var/www/html/hsirb/        # Web directory (Apache serves from here)
├── static/                 # Static files (copied from staticfiles/)
├── media/                  # Media files (user uploads)
└── hsirb-system.sock      # Gunicorn Unix socket

/etc/httpd/conf.d/
└── hsirb.conf              # Apache configuration

/etc/systemd/system/
└── hsirb-system.service    # Gunicorn systemd service
```

## 🔄 Updating the Application

Simply run:

```bash
./deploy-to-server.sh
```

This will:
1. Pull latest code from GitHub
2. Update Python dependencies
3. Run database migrations
4. Collect static files
5. Copy static files to web directory
6. Restart Gunicorn service

**Note:** Apache restart is usually not needed unless you change Apache config.

## 🐛 Troubleshooting

### Service Not Starting

```bash
# Check status
ssh bayoupal 'sudo systemctl status hsirb-system'

# View recent logs
ssh bayoupal 'sudo journalctl -u hsirb-system -n 50'

# Follow logs in real-time
ssh bayoupal 'sudo journalctl -u hsirb-system -f'
```

**Common issues:**
- Missing `.env` file → Create it from template
- Wrong database password → Check `~/hsirb-db-password.txt`
- Permission issues → See permission fixes below

### Apache Errors

```bash
# Test Apache configuration
ssh bayoupal 'sudo httpd -t'

# View error logs
ssh bayoupal 'sudo tail -f /var/log/httpd/hsirb_error.log'

# View access logs
ssh bayoupal 'sudo tail -f /var/log/httpd/hsirb_access.log'
```

**Common issues:**
- Config syntax error → Check `/etc/httpd/conf.d/hsirb.conf`
- Module not loaded → Check if proxy modules are enabled
- SSL certificate issues → Verify cert paths

### Database Connection Issues

```bash
# Test connection
ssh bayoupal
psql -U hsirb_user -d hsirb_db -h localhost
# Enter password when prompted (from ~/hsirb-db-password.txt)

# Check PostgreSQL is running
ssh bayoupal 'sudo systemctl status postgresql'
```

**Common issues:**
- PostgreSQL not running → `sudo systemctl start postgresql`
- Wrong password → Check `.env` file matches `~/hsirb-db-password.txt`
- Database doesn't exist → Run `setup-postgresql.sh` again

### Permission Issues

```bash
ssh bayoupal

# Fix application directory permissions
echo "nsutemppasswd123" | sudo -S chown -R apache:apache ~/hsirb-system
echo "nsutemppasswd123" | sudo -S chmod -R 755 ~/hsirb-system

# Fix web directory permissions
echo "nsutemppasswd123" | sudo -S chown -R apache:apache /var/www/html/hsirb
echo "nsutemppasswd123" | sudo -S chmod -R 755 /var/www/html/hsirb

# Fix socket permissions (if exists)
echo "nsutemppasswd123" | sudo -S chown apache:apache /var/www/html/hsirb/hsirb-system.sock
```

### Static Files Not Loading

```bash
ssh bayoupal
cd ~/hsirb-system
source venv/bin/activate

# Recollect static files
python manage.py collectstatic --noinput

# Copy to web directory
echo "nsutemppasswd123" | sudo -S cp -r staticfiles/* /var/www/html/hsirb/static/
echo "nsutemppasswd123" | sudo -S chown -R apache:apache /var/www/html/hsirb/static
```

## 📊 Useful Commands

### Service Management

```bash
# Start/Stop/Restart Gunicorn
ssh bayoupal 'echo "nsutemppasswd123" | sudo -S systemctl start hsirb-system'
ssh bayoupal 'echo "nsutemppasswd123" | sudo -S systemctl stop hsirb-system'
ssh bayoupal 'echo "nsutemppasswd123" | sudo -S systemctl restart hsirb-system'

# Check status
ssh bayoupal 'sudo systemctl status hsirb-system'

# View logs
ssh bayoupal 'sudo journalctl -u hsirb-system -f'
```

### Apache Management

```bash
# Restart Apache
ssh bayoupal 'echo "nsutemppasswd123" | sudo -S systemctl restart httpd'

# Test configuration
ssh bayoupal 'sudo httpd -t'

# View logs
ssh bayoupal 'sudo tail -f /var/log/httpd/hsirb_error.log'
```

### Django Management

```bash
ssh bayoupal
cd ~/hsirb-system
source venv/bin/activate

# Django shell
python manage.py shell

# Create superuser
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Check for issues
python manage.py check
```

### Database Management

```bash
ssh bayoupal

# Connect to database
psql -U hsirb_user -d hsirb_db -h localhost

# View database password
cat ~/hsirb-db-password.txt

# Backup database
pg_dump -U hsirb_user -d hsirb_db > ~/hsirb_backup_$(date +%Y%m%d).sql
```

## 🔒 Security Notes

- ✅ SSL/TLS enabled via shared certificate (`/etc/ssl/certs/platform.crt`)
- ✅ Database password stored in `.env` (not in git)
- ✅ SECRET_KEY in `.env` (not in git)
- ✅ DEBUG=False in production
- ✅ Static files served by Apache (not Django)
- ✅ Gunicorn running as `apache` user (limited permissions)
- ✅ Database password also saved to `~/hsirb-db-password.txt` (chmod 600)

## 🔄 Deployment Workflow

### Initial Deployment

1. Run `setup-postgresql.sh` → Creates database
2. Run `setup-apache-site.sh` → Configures Apache
3. Run `setup-gunicorn-service.sh` → Sets up Gunicorn service
4. Run `deploy-to-server.sh` → Deploys code
5. Create `.env` file on server
6. Run migrations and create superuser
7. Start services

### Regular Updates

1. Make changes locally
2. Commit and push to GitHub
3. Run `./deploy-to-server.sh`
4. Done! (Service auto-restarts)

## 📞 Support

For issues, check in this order:

1. **Service logs:** `sudo journalctl -u hsirb-system -n 100`
2. **Apache logs:** `/var/log/httpd/hsirb_error.log`
3. **Django check:** `python manage.py check`
4. **Database connection:** `psql -U hsirb_user -d hsirb_db`
5. **File permissions:** Check ownership with `ls -la`

## 🎯 Quick Reference

**URL:** https://bayoupal.nicholls.edu/hsirb/

**SSH:** `ssh bayoupal`

**Deploy:** `./deploy-to-server.sh`

**Restart service:** `ssh bayoupal 'echo "nsutemppasswd123" | sudo -S systemctl restart hsirb-system'`

**View logs:** `ssh bayoupal 'sudo journalctl -u hsirb-system -f'`

---

**Your HSIRB Study Management System is now ready for deployment!** 🚀
