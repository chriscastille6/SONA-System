# 🚀 RHEL 10 Quick Start Guide

**Fast-track deployment for your campus RHEL 10 VM.**

---

## ⚡ Quick Setup (If I Have SSH Access)

If you provide SSH access, I can:
1. ✅ Run the automated setup script
2. ✅ Configure PostgreSQL
3. ✅ Deploy your application
4. ✅ Set up Gunicorn and Nginx
5. ✅ Configure SELinux
6. ✅ Test the deployment

**Just provide:**
- Server IP address
- SSH username
- SSH key or password
- Domain name (or IP is fine)

---

## 📋 Manual Quick Start

### 1. Run Automated Setup Script

```bash
# On your RHEL server
cd /tmp
wget https://raw.githubusercontent.com/chriscastille6/SONA-System/main/rhel_setup.sh
# Or copy the file to server
chmod +x rhel_setup.sh
sudo ./rhel_setup.sh
```

### 2. Configure PostgreSQL

```bash
# Edit pg_hba.conf
sudo nano /var/lib/pgsql/data/pg_hba.conf
# Change 'ident' to 'md5' for local connections

sudo systemctl restart postgresql

# Create database
sudo -u postgres psql << EOF
CREATE DATABASE sona_db;
CREATE USER sona_user WITH PASSWORD 'your-password';
ALTER ROLE sona_user SET client_encoding TO 'utf8';
ALTER ROLE sona_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE sona_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE sona_db TO sona_user;
\q
EOF
```

### 3. Deploy Application

```bash
cd /var/www/sona-system
git clone https://github.com/chriscastille6/SONA-System.git .
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
nano .env
# Add your configuration (see RHEL_DEPLOYMENT_GUIDE.md)
```

### 5. Initialize Database

```bash
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 6. Set Up Gunicorn Service

```bash
sudo nano /etc/systemd/system/sona-system.service
# Copy content from RHEL_DEPLOYMENT_GUIDE.md

sudo systemctl daemon-reload
sudo systemctl start sona-system
sudo systemctl enable sona-system
```

### 7. Configure Nginx

```bash
sudo nano /etc/nginx/conf.d/sona-system.conf
# Copy content from RHEL_DEPLOYMENT_GUIDE.md

sudo nginx -t
sudo systemctl reload nginx
```

### 8. Configure SELinux

```bash
sudo setsebool -P httpd_can_network_connect 1
sudo setsebool -P httpd_read_user_content 1
sudo semanage fcontext -a -t httpd_sys_content_t "/var/www/sona-system(/.*)?"
sudo restorecon -Rv /var/www/sona-system
```

### 9. Test!

```bash
curl http://localhost
# Or visit http://your-server-ip in browser
```

---

## 🔑 Key RHEL-Specific Commands

```bash
# Package management
sudo dnf install package-name
sudo dnf update

# Services
sudo systemctl start service-name
sudo systemctl status service-name

# Firewall
sudo firewall-cmd --list-all
sudo firewall-cmd --reload

# SELinux
getenforce
sudo setenforce 0  # Permissive (for testing)

# Logs
sudo journalctl -u sona-system -f
```

---

## 🆘 Common Issues

### SELinux Blocking Access?
```bash
sudo setenforce 0  # Temporarily disable
# Then configure properly (see guide)
```

### Can't Connect to Database?
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check pg_hba.conf
sudo cat /var/lib/pgsql/data/pg_hba.conf
```

### Permission Denied?
```bash
sudo chown -R apache:apache /var/www/sona-system
sudo restorecon -Rv /var/www/sona-system
```

---

## 📞 Need Help?

**Full guide:** See `RHEL_DEPLOYMENT_GUIDE.md` for complete instructions.

**Or provide SSH access** and I can deploy it for you!
