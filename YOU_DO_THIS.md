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

On the server (still in `~/hsirb-system`):

```bash
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

**Full walkthrough:** See **DEPLOYMENT_START_HERE.md**.
