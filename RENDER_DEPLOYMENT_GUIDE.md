# 🚀 Render Deployment Guide for SONA System

**Render** is the easiest migration path from Railway. This guide will get you deployed in ~10 minutes.

---

## ✅ Prerequisites

- GitHub account (you already have: `chriscastille6/SONA-System`)
- Render account (free signup: https://render.com)

---

## 📋 Step 1: Sign Up for Render

1. Go to **https://render.com**
2. Click **"Get Started for Free"**
3. Sign up with **GitHub** (recommended - easiest)
4. Authorize Render to access your repositories

---

## 🗄️ Step 2: Create PostgreSQL Database

1. In Render Dashboard, click **"+ New"**
2. Select **"PostgreSQL"**
3. Configure:
   - **Name:** `sona-database` (or any name)
   - **Database:** `sona_db` (or any name)
   - **User:** Auto-generated (or custom)
   - **Region:** Choose closest to you
   - **PostgreSQL Version:** 16 (latest)
   - **Plan:** **Free** ✅
4. Click **"Create Database"**
5. **Save the connection string!** (You'll need it in Step 4)

---

## 🌐 Step 3: Create Web Service

1. In Render Dashboard, click **"+ New"**
2. Select **"Web Service"**
3. Connect your GitHub repository:
   - Select **"chriscastille6/SONA-System"**
   - Click **"Connect"**
4. Configure the service:

   **Basic Settings:**
   - **Name:** `sona-system` (or any name)
   - **Region:** Same as database
   - **Branch:** `main`
   - **Root Directory:** (leave empty)
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`

   **Plan:**
   - Select **Free** ✅

5. Click **"Advanced"** to add environment variables (Step 4)

---

## 🔐 Step 4: Set Environment Variables

In the Web Service configuration, scroll to **"Environment Variables"** and add:

### Required Variables:

```bash
# Database (from PostgreSQL service)
DATABASE_URL=<your-postgres-connection-string>

# Django Settings
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
DEBUG=False
ALLOWED_HOSTS=.onrender.com

# Site Configuration
SITE_NAME=Research Participant System
INSTITUTION_NAME=Nicholls State University
SITE_URL=https://your-app-name.onrender.com

# Email (Console for now - update later)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@nicholls.edu

# Celery (In-memory for free tier)
CELERY_BROKER_URL=memory://
CELERY_RESULT_BACKEND=memory://
```

### Optional (for demo data):

```bash
DJANGO_SUPERUSER_EMAIL=admin@nicholls.edu
DJANGO_SUPERUSER_PASSWORD=changeme123
```

**How to get DATABASE_URL:**
1. Go to your PostgreSQL service in Render
2. Click on **"Connections"** tab
3. Copy the **"Internal Database URL"** (for same service) or **"External Database URL"** (if needed)
4. Paste as `DATABASE_URL` value

---

## 🚀 Step 5: Deploy!

1. Scroll down and click **"Create Web Service"**
2. Render will:
   - ✅ Clone your repo
   - ✅ Install dependencies
   - ✅ Run migrations (if configured)
   - ✅ Collect static files
   - ✅ Start the server

3. **Wait 3-5 minutes** for first deployment

---

## 🔧 Step 6: Configure Auto-Deploy (Optional)

Render automatically deploys on every `git push` to your main branch. This is enabled by default!

To verify:
1. Go to your Web Service
2. Click **"Settings"** tab
3. Under **"Auto-Deploy"**, ensure it's enabled

---

## 📝 Step 7: Update Settings for Render

I'll update your `config/settings.py` to support Render. The changes needed:

1. Add `.onrender.com` to `ALLOWED_HOSTS`
2. Ensure static files are handled correctly
3. Configure for Render's proxy

**I can make these changes for you!**

---

## 🌍 Step 8: Get Your Public URL

1. Once deployment completes, go to your Web Service
2. Click **"Settings"** tab
3. Under **"Custom Domain"**, you'll see your default URL:
   - Format: `https://your-app-name.onrender.com`
4. **That's your live site!** 🎉

---

## 🔄 Step 9: Update Code for Render

After deployment, I'll help you:
1. Update `config/settings.py` to support Render
2. Ensure `Procfile` works with Render
3. Test the deployment

---

## ⚠️ Important Notes

### Free Tier Limitations:

1. **Spins down after 15 minutes of inactivity**
   - First request after sleep takes ~30 seconds
   - Subsequent requests are fast
   - **Solution:** Use a free uptime monitor (like UptimeRobot) to ping every 10 minutes

2. **750 hours/month**
   - Enough for always-on if you keep it awake
   - Or ~31 days of 24/7 uptime

3. **100 GB bandwidth/month**
   - Usually plenty for low-medium traffic

### Keep It Awake (Optional):

Use a free service like **UptimeRobot** (https://uptimerobot.com):
1. Sign up (free)
2. Add monitor for your Render URL
3. Set interval to 10 minutes
4. Your app stays awake! ✅

---

## 🐛 Troubleshooting

### Build Failed?

1. **Check logs** in Render Dashboard → Your Service → Logs
2. **Common issues:**
   - Missing `SECRET_KEY` → Add to environment variables
   - Database connection error → Check `DATABASE_URL`
   - Port error → Use `$PORT` in start command (already done above)

### App Not Loading?

1. **Check environment variables** are set correctly
2. **Verify `ALLOWED_HOSTS`** includes `.onrender.com`
3. **Check logs** for error messages
4. **Wait a few minutes** after first deployment

### Database Connection Issues?

1. Use **Internal Database URL** (if services are in same region)
2. Or use **External Database URL** with proper credentials
3. Ensure PostgreSQL service is running

---

## 📊 What Happens on Deploy

Render automatically:
1. ✅ Clones your GitHub repo
2. ✅ Installs Python dependencies
3. ✅ Runs `python manage.py migrate` (if in Procfile release)
4. ✅ Collects static files
5. ✅ Starts Gunicorn server
6. ✅ Loads demo data (if configured)

---

## 🔄 Updating Your App

**Same as Railway!** Just push to GitHub:

```bash
cd "/Users/ccastille/Documents/GitHub/SONA System"
git add -A
git commit -m "Your changes"
git push
```

Render automatically redeploys! 🚀

---

## 💰 Cost

**FREE!** ✅

Render free tier includes:
- ✅ 750 hours/month
- ✅ Free PostgreSQL
- ✅ Free SSL certificates
- ✅ Auto-deploy from GitHub
- ✅ Unlimited deploys

**Upgrade later** if you need:
- Always-on (no sleep) - $7/month
- More resources - $7-25/month

---

## 🎯 Quick Checklist

- [ ] Sign up for Render
- [ ] Create PostgreSQL database
- [ ] Create Web Service
- [ ] Set environment variables
- [ ] Deploy
- [ ] Get public URL
- [ ] (Optional) Set up uptime monitor
- [ ] Test your live site!

---

## 🆘 Need Help?

- **Render Docs:** https://render.com/docs
- **Render Discord:** https://render.com/discord
- **Render Status:** https://status.render.com

---

**Ready to deploy?** Follow the steps above and you'll have your SONA system live on Render in ~10 minutes! 🚀
