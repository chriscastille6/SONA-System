# 🚂 Railway Deployment Guide

## Quick Deploy to Railway (5 minutes)

Railway is a free hosting platform perfect for sharing your SONA demo. Your app will get a permanent public URL like `https://sona-system.railway.app`

---

## Step 1: Create Railway Account

1. Go to **https://railway.app**
2. Click **"Start a New Project"** or **"Login"**
3. Sign up with GitHub (recommended) or email

---

## Step 2: Create GitHub Repository

You need to push your code to GitHub first (Railway deploys from GitHub):

### Option A: Using GitHub Desktop (Easiest)
1. Download **GitHub Desktop** from https://desktop.github.com
2. Open GitHub Desktop
3. Click **File → Add Local Repository**
4. Select your SONA System folder
5. Click **Publish repository**
6. Uncheck "Keep this code private" (or keep it private, your choice)
7. Click **Publish Repository**

### Option B: Using Command Line
```bash
# 1. Create a new repository on GitHub.com (click the + button)
# Name it: SONA-System

# 2. Add the remote and push:
cd "/Users/ccastille/Documents/GitHub/SONA System"
git remote add origin https://github.com/YOUR_USERNAME/SONA-System.git
git branch -M main
git push -u origin main
```

---

## Step 3: Deploy on Railway

1. **Go to Railway Dashboard:** https://railway.app/dashboard

2. **Click "New Project"**

3. **Select "Deploy from GitHub repo"**

4. **Choose your SONA-System repository**

5. **Railway will automatically detect Django and start deploying!**

---

## Step 4: Add PostgreSQL Database

1. In your Railway project, click **"+ New"**

2. Select **"Database" → "PostgreSQL"**

3. Railway automatically links it to your Django app! ✨

---

## Step 5: Set Environment Variables

Click on your Django service, then go to **"Variables"** tab:

### Required Variables:

```bash
DEBUG=False
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
ALLOWED_HOSTS=.railway.app
```

### Optional (but recommended):

```bash
DJANGO_SUPERUSER_EMAIL=admin@nicholls.edu
DJANGO_SUPERUSER_PASSWORD=changeme123
```

**Tip:** Railway automatically provides `DATABASE_URL` from the PostgreSQL service!

---

## Step 6: Wait for Deployment

Railway will:
1. ✅ Install dependencies from `requirements.txt`
2. ✅ Run database migrations
3. ✅ Collect static files
4. ✅ **Automatically load demo data!** (via Procfile)
5. ✅ Start the server

This takes about 2-3 minutes.

---

## Step 7: Get Your Public URL

1. Once deployed, go to **"Settings"** tab
2. Scroll to **"Domains"**
3. Click **"Generate Domain"**
4. Railway will give you a URL like: `https://sona-system-production.railway.app`

**🎉 That's your shareable demo link!**

---

## Step 8: Share with Your Colleague

Send them:
- **URL:** Your Railway domain
- **Login credentials:**
  - Researcher: researcher@nicholls.edu / demo123
  - Instructor: instructor@nicholls.edu / demo123
  - Student: emily.johnson@my.nicholls.edu / demo123

The demo data is automatically loaded, so they can start exploring immediately!

---

## 🔧 Troubleshooting

### Build Failed?

Check the logs in Railway dashboard. Common issues:

1. **Missing SECRET_KEY**: Add it in Variables tab
2. **Database error**: Make sure PostgreSQL service is added
3. **Port error**: Railway automatically sets PORT, you don't need to configure it

### Need to Update Code?

Just push to GitHub:
```bash
git add -A
git commit -m "Updated something"
git push
```

Railway automatically redeploys! 🚀

---

## 💰 Cost

**FREE for demos!**

Railway free tier includes:
- ✅ 500 hours/month (always-on for ~20 days)
- ✅ Up to $5 usage credit
- ✅ Perfect for demos and testing

For permanent hosting, upgrade to hobby plan ($5-10/month).

---

## 🔒 Security Note

The demo data includes:
- Pre-created users with simple passwords (demo123)
- Sample research data
- Test credit transactions

**For production use:**
- Change all passwords
- Remove demo data: `python manage.py flush`
- Set strong SECRET_KEY
- Enable HTTPS (Railway does this automatically)
- Review security settings in settings.py

---

## 📊 What Your Colleague Will See

Once deployed, your Railway instance includes:
- ✅ Full SONA system running
- ✅ 15 demo users (researcher, instructor, 12 students)
- ✅ 1 complete study with 45 timeslots
- ✅ 23 signups (past and future)
- ✅ 12 protocol responses with data
- ✅ Credit tracking system
- ✅ All features functional

---

## Alternative: Use Railway CLI

If you prefer command line:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create project and deploy
railway init
railway up
railway open
```

---

## 🎯 Quick Summary

1. ✅ Push code to GitHub
2. ✅ Create Railway account
3. ✅ Connect GitHub repo to Railway
4. ✅ Add PostgreSQL database
5. ✅ Set environment variables (SECRET_KEY, DEBUG=False)
6. ✅ Generate domain
7. ✅ Share URL with colleague

**Total time: ~5 minutes**

---

## Need Help?

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Railway Templates: https://railway.app/templates

---

**Ready to deploy?** Follow the steps above and you'll have a live demo in minutes! 🚀

