# What You Need To Do

Everything that could be done in the repo is done. Do the following in order.

---

## 1. Push to GitHub

Commit and push so the server can pull the latest (fixed requirements, scripts, docs):

```bash
cd "/Users/ccastille/Documents/GitHub/SONA System"
git add -A
git status   # review
git commit -m "Deployment fixes: django-celery-results, sudo subshells, deployment docs"
git push origin main
```

---

## 2. (Optional) Create migrations locally

If the server reported "models in accounts, courses have changes not reflected in a migration", create migrations and push:

```bash
source venv/bin/activate
python manage.py makemigrations accounts courses
git add apps/accounts/migrations apps/courses/migrations
git commit -m "Add migrations for accounts, courses"
git push origin main
```

If `makemigrations` says "No changes detected", skip this step.

---

## 3. Deploy to the server

From the same project directory:

```bash
./deploy-to-server.sh
```

If the script still can’t run sudo (e.g. wrong server password), that’s OK—code and static files will be updated. You’ll do the sudo steps in step 5.

---

## 4. First-time only: set up .env on the server

SSH in and create `.env` from the template:

```bash
ssh bayoupal
cd ~/hsirb-system
cp env.template .env
nano .env
```

Set at least:

- **SECRET_KEY** – Generate: `python3 -c "import secrets; print(secrets.token_urlsafe(50))"` (run on Mac or server), paste into .env.
- **DEBUG=False**
- **ALLOWED_HOSTS** – Must include `bayoupal.nicholls.edu`.
- **DATABASE_URL** – Use the value from when you ran `setup-postgresql.sh`. If the password contains `=` or `/`, URL-encode: `=` → `%3D`, `/` → `%2F`.  
  Example: `postgresql://hsirb_user:bMUl4RK4BfUj8vB0C3M6VnnvBNtPS3mD%2Fx8qT%2B%2BjGss%3D@localhost:5432/hsirb_db`

Save and exit (nano: Ctrl+O, Enter, Ctrl+X).

---

## 5. First-time only: migrate and create admin user

On the server, **go into the app directory first** (otherwise `manage.py` is not found):

```bash
cd ~/hsirb-system
source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
```

Use your admin email and a strong password.

---

## 6. Restart services (if the deploy script didn’t run sudo)

If the deploy script couldn’t run sudo, do this on the server:

```bash
# Copy static files
cd ~/hsirb-system && source venv/bin/activate
python manage.py collectstatic --noinput
echo 'nsutemppasswd123' | sudo -S mkdir -p /var/www/html/hsirb/static
echo 'nsutemppasswd123' | sudo -S cp -r staticfiles/* /var/www/html/hsirb/static/
echo 'nsutemppasswd123' | sudo -S chown -R apache:apache /var/www/html/hsirb/static

# Restart app and web server
echo 'nsutemppasswd123' | sudo -S systemctl restart hsirb-system
echo 'nsutemppasswd123' | sudo -S systemctl restart httpd
```

*(If your server’s sudo password is different, use that instead of `nsutemppasswd123`.)*

---

## 7. Test

Open: **https://bayoupal.nicholls.edu/hsirb/**

You should see the HSIRB homepage. Log in with the superuser you created.

---

## Password issues (what you’re seeing)

You’re hitting two different “password” problems:

### 1. Database: “password authentication failed for user hsirb_user”

The app on the server is using a wrong or unset **DATABASE_URL**. Fix it on the server.

**Option A – Generate the correct line (recommended):** On the server, run one of these. Each reads the saved password and prints a ready-to-paste `DATABASE_URL` line with proper URL encoding.

Using the project script (from repo):

```bash
cd ~/hsirb-system
python3 scripts/generate_database_url.py
```

Or a one-liner (no repo script):

```bash
python3 -c "
from urllib.parse import quote_plus
with open('/home/ccastille/hsirb-db-password.txt') as f:
    p = f.read().strip()
print('DATABASE_URL=postgresql://hsirb_user:' + quote_plus(p) + '@localhost:5432/hsirb_db')
"
```

Copy the single line it prints, then:

```bash
cd ~/hsirb-system
nano .env
```

Paste that line (or set `DATABASE_URL=` and paste the value after the `=`). Remove any old `DATABASE_URL` line. Save (Ctrl+O, Enter, Ctrl+X).

**Option B – Manual:** Ensure **DATABASE_URL** in `.env` uses the password from `cat ~/hsirb-db-password.txt`. If the password contains **`=`** or **`/`**, URL-encode: `=` → **%3D**, `/` → **%2F**, `+` → **%2B**.

Save, then run migrations again (from the app directory):

```bash
cd ~/hsirb-system
source venv/bin/activate
python manage.py migrate
```

**If it still fails after updating .env:**

1. **Check what Django is using** (on the server, from `~/hsirb-system` with venv active):

   ```bash
   cd ~/hsirb-system && source venv/bin/activate && python -c "
   import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
   import django; django.setup()
   from django.conf import settings
   d = settings.DATABASES['default']
   print('Django DB:', d.get('USER'), '@', d.get('HOST'), '/', d.get('NAME'))
   "
   ```

   You should see `Django DB: hsirb_user @ localhost / hsirb_db`. If you see something else, `.env` was not being read; after you deploy the latest code, settings will load `.env` from the project root.

2. **Make PostgreSQL use the same password as the file** (in case the DB user was created with a different password). On the server:

   ```bash
   sudo -u postgres psql -d postgres -c "ALTER USER hsirb_user WITH PASSWORD '$(cat ~/hsirb-db-password.txt | sed "s/'/''/g")';"
   ```

   **If you get “Password for user postgres”** and you don’t know the postgres DB password, allow local **peer** auth so `sudo -u postgres psql` doesn’t ask for a password:

   - Find `pg_hba.conf` (no DB login needed): `sudo find /var/lib /usr -name pg_hba.conf 2>/dev/null` — often `/var/lib/pgsql/15/data/pg_hba.conf` or `/var/lib/pgsql/data/pg_hba.conf`.
   - **Back it up:** `sudo cp /path/to/pg_hba.conf /path/to/pg_hba.conf.bak` (use the path you found).
   - Edit `pg_hba.conf` with `sudo nano /path/to/pg_hba.conf`.
   - Change the line for local connections so it uses **peer** (not `md5`/`scram-sha-256`). For example change:
     - `local   all   postgres   scram-sha-256` → `local   all   postgres   peer`
     - or add a line: `local   all   postgres   peer` and comment out the existing `local ... postgres` line.
   - Restart PostgreSQL: `sudo systemctl restart postgresql`
   - Run the `ALTER USER hsirb_user ...` command again (no password prompt).
   - (Optional) Restore the original auth and restart: `sudo cp /var/lib/pgsql/15/data/pg_hba.conf.bak /var/lib/pgsql/15/data/pg_hba.conf` and `sudo systemctl restart postgresql`

   Then run `python manage.py migrate` again from `~/hsirb-system` with venv active.

### 2. Sudo: “password for ccastille: Sorry, try again”

The deploy script pipes `nsutemppasswd123` into `sudo`. That only works if **that is actually the sudo password for user ccastille on bayoupal**.

- If your **server** sudo password is different, either:
  - **Option A:** In `deploy-to-server.sh`, change the line `SUDO_PASS="nsutemppasswd123"` to your real server sudo password (don’t commit that if the repo is shared), or  
  - **Option B:** Ignore the script’s sudo errors and do step 6 **manually**: SSH to bayoupal and run those same commands by hand; when it says `[sudo] password for ccastille:`, type **your server sudo password** (the one that works when you SSH in and run `sudo something`).

---

**Full walkthrough:** See **DEPLOYMENT_START_HERE.md**.
