# HSIRB Deployment: Start Here

Step-by-step guide to get the HSIRB Study Management System running on **bayoupal.nicholls.edu** at **https://bayoupal.nicholls.edu/hsirb/**.

---

## What You Need Before Starting

- **SSH access** to bayoupal: `ssh bayoupal` (or `ssh ccastille@bayoupal.nicholls.edu`)
- **Sudo password** for the server: `nsutemppasswd123`
- **GitHub**: Your code pushed to the repo (e.g. `chriscastille6/SONA-System`). If the repo is **private**, the server needs access (see “Private repo” below).

---

## Private Repo (If Applicable)

If the GitHub repo is private, bayoupal must authenticate before it can `git clone` or `git pull`:

1. **On your Mac**, generate a **deploy key** (or use an existing one for the server):
   ```bash
   ssh-keygen -t ed25519 -C "bayoupal-hsirb" -f ~/.ssh/bayoupal_deploy -N ""
   ```
2. **On GitHub**: Repo → **Settings** → **Deploy keys** → **Add deploy key**. Paste the contents of `~/.ssh/bayoupal_deploy.pub`. Optionally name it “bayoupal”.
3. **On bayoupal** (after first SSH):
   ```bash
   ssh bayoupal
   mkdir -p ~/.ssh
   # On your Mac, show the private key: cat ~/.ssh/bayoupal_deploy
   # On bayoupal, create ~/.ssh/id_ed25519 (or id_rsa) and paste the private key, then:
   chmod 600 ~/.ssh/id_ed25519
   ```
4. **Change the deploy script** to use SSH for Git: in `deploy-to-server.sh`, the clone URL should be `git@github.com:chriscastille6/SONA-System.git` (not `https://...`) when using a deploy key.

If you use **HTTPS + Personal Access Token** instead, configure Git credentials on the server (e.g. `git config credential.helper store` and one `git pull` with the token).

---

## One-Time Server Setup (Do Once)

Run these **from your Mac**, in the **SONA System** project directory.

### 1. PostgreSQL (database)

```bash
chmod +x setup-postgresql.sh
./setup-postgresql.sh
```

**Save the database password** shown at the end. It is also written on the server to `~/hsirb-db-password.txt`.

### 2. Apache (web server / reverse proxy)

```bash
chmod +x setup-apache-site.sh
./setup-apache-site.sh
```

### 3. Gunicorn (Django app server)

```bash
chmod +x setup-gunicorn-service.sh
./setup-gunicorn-service.sh
```

---

## Deploy the Application

From your Mac, in the **SONA System** directory:

```bash
./deploy-to-server.sh
```

This will:

- Clone (or pull) the repo into `~/hsirb-system` on bayoupal
- Create a Python venv and install dependencies
- Run migrations
- Collect static files
- Copy static files to the web directory
- Try to restart the Gunicorn service (may prompt for sudo password)

If the script asks for a **sudo password**, enter: `nsutemppasswd123`.  
If you can’t enter a password (e.g. non-interactive run), the script will still do clone/pull, install, migrate, and collectstatic; you’ll do the sudo steps manually on the server (see below).

---

## Configure Environment (First Time or After Changing Secrets)

1. SSH to the server:
   ```bash
   ssh bayoupal
   ```

2. Go to the app and copy the env template:
   ```bash
   cd ~/hsirb-system
   cp env.template .env
   nano .env
   ```

3. Set at least these in `.env`:

   - **SECRET_KEY**  
     Generate one (e.g. on your Mac or on the server):
     ```bash
     python3 -c "import secrets; print(secrets.token_urlsafe(50))"
     ```
     Paste the output as the value of `SECRET_KEY`.

   - **DEBUG=False**

   - **ALLOWED_HOSTS**  
     Include `bayoupal.nicholls.edu` (e.g. `bayoupal.nicholls.edu,localhost`).

   - **DATABASE_URL**  
     Format: `postgresql://hsirb_user:YOUR_DB_PASSWORD@localhost:5432/hsirb_db`  
     Get the password from the server: `cat ~/hsirb-db-password.txt`

   - **Email** (optional): `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, etc., if you want PI/notification emails.

4. Save and exit (`Ctrl+O`, Enter, `Ctrl+X` in nano).

---

## First-Time Database and Admin User

On the server:

```bash
ssh bayoupal
cd ~/hsirb-system
source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
```

Use the prompts to set an admin email and password.

---

## Start or Restart Services

If the deploy script didn’t run the sudo steps (e.g. no password entered), do them on the server:

```bash
ssh bayoupal
# Copy static files (if not already done)
cd ~/hsirb-system && source venv/bin/activate
python manage.py collectstatic --noinput
echo 'nsutemppasswd123' | sudo -S mkdir -p /var/www/html/hsirb/static
echo 'nsutemppasswd123' | sudo -S cp -r staticfiles/* /var/www/html/hsirb/static/
echo 'nsutemppasswd123' | sudo -S chown -R apache:apache /var/www/html/hsirb/static

# Restart Gunicorn and Apache
echo 'nsutemppasswd123' | sudo -S systemctl restart hsirb-system
echo 'nsutemppasswd123' | sudo -S systemctl restart httpd
```

From your Mac you can also restart only the app:

```bash
ssh bayoupal 'echo "nsutemppasswd123" | sudo -S systemctl restart hsirb-system'
```

---

## Check That It’s Working

1. **Site:** Open **https://bayoupal.nicholls.edu/hsirb/** in a browser. You should see the HSIRB homepage.

2. **App service:**
   ```bash
   ssh bayoupal 'sudo systemctl status hsirb-system'
   ```
   Should show “active (running)”.

3. **Django check (on server):**
   ```bash
   ssh bayoupal
   cd ~/hsirb-system && source venv/bin/activate
   python manage.py check
   ```
   Should report no issues.

---

## Later: Deploying Updates

1. Commit and push your changes to GitHub (e.g. `main`).
2. From your Mac, in the SONA System directory:
   ```bash
   ./deploy-to-server.sh
   ```
3. If the script didn’t restart Gunicorn (no sudo password), SSH and run:
   ```bash
   ssh bayoupal 'echo "nsutemppasswd123" | sudo -S systemctl restart hsirb-system'
   ```

---

## Quick Reference

| What | Command / URL |
|------|----------------|
| App URL | https://bayoupal.nicholls.edu/hsirb/ |
| SSH | `ssh bayoupal` |
| Deploy from Mac | `./deploy-to-server.sh` |
| Restart app | `ssh bayoupal 'echo "nsutemppasswd123" \| sudo -S systemctl restart hsirb-system'` |
| App logs | `ssh bayoupal 'sudo journalctl -u hsirb-system -f'` |
| DB password file | On server: `cat ~/hsirb-db-password.txt` |

---

## If You Saw These Errors

**1. `django-celery-results==2.5.3` / "No matching distribution found"**  
The repo’s `requirements.txt` was updated to use `2.5.1` (2.5.3 doesn’t exist). Push the latest code and run `./deploy-to-server.sh` again so the server gets the fix.

**2. "sudo: no password was provided" when running scripts from your Mac**  
The scripts pipe the server sudo password (`nsutemppasswd123`) into `sudo -S`. If your **server’s** sudo password is different, either:
- Change the `SUDO_PASS="nsutemppasswd123"` line inside each script to match the real server password, or  
- Run the sudo steps by hand on the server (see “Start or Restart Services” above).

**3. "Your models in 'accounts', 'courses' have changes not reflected in a migration"**  
From your Mac (with venv activated):  
`python manage.py makemigrations accounts courses`  
Then commit, push, and run `./deploy-to-server.sh` again so the server runs the new migrations.

**4. DATABASE_URL password contains `=` or special characters**  
If the DB password has `=` (e.g. from openssl rand -base64), URL-encode it in `.env`: use `%3D` for `=`, `%2F` for `/`, etc. Example:  
`postgresql://hsirb_user:bMUl4RK4BfUj8vB0C3M6VnnvBNtPS3mD%2Fx8qT%2B%2BjGss%3D@localhost:5432/hsirb_db`

**5. hsirb-system.service fails with "Permission denied" / status 203/EXEC (SELinux)**  
On RHEL/CentOS/Fedora with SELinux enforcing, systemd may be blocked from executing the venv in your home directory. Fix it on the server:

```bash
# One-time: install SELinux tools if needed
sudo dnf install -y policycoreutils-python-utils   # or yum on older systems

# Run the fix (from the repo on the server)
cd ~/hsirb-system
sudo bash scripts/fix-selinux-venv.sh

# Re-enable SELinux if you had set it to permissive for testing
sudo setenforce 1
sudo systemctl restart hsirb-system
```

Remove any temporary override that runs the service unconfined:  
`sudo rm /etc/systemd/system/hsirb-system.service.d/selinux.conf`  
(and `override.conf` if you only added it for this issue).

For more detail (troubleshooting, Apache, permissions), see **HSIRB_DEPLOYMENT_GUIDE.md**.
