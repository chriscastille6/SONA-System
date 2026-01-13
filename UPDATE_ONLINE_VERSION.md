# 🔄 How to Update the Online SONA System

Your SONA system is deployed on **Railway** and connected to a **GitHub repository**. Here are the methods to update the online version:

---

## Method 1: GitHub Push (Recommended - Automatic Redeploy)

This is the **easiest and most common** method. Railway automatically redeploys when you push to GitHub.

### Steps:

1. **Make your changes locally** (like you just did with the institution name)

2. **Commit your changes:**
   ```bash
   cd "/Users/ccastille/Documents/GitHub/SONA System"
   git add -A
   git commit -m "Updated institution name to Nicholls State University"
   ```

3. **Push to GitHub:**
   ```bash
   git push
   ```

4. **Railway automatically redeploys!** 🚀
   - Railway detects the push
   - Runs migrations
   - Collects static files
   - Restarts the server
   - Takes about 2-3 minutes

5. **Check deployment status:**
   - Go to https://railway.app/dashboard
   - Click on your SONA System project
   - View the "Deployments" tab to see progress

---

## Method 2: Railway CLI (Alternative)

If you prefer command-line tools or need more control:

### Setup (one-time):

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login
```

### Update Process:

```bash
cd "/Users/ccastille/Documents/GitHub/SONA System"

# Link to your Railway project (if not already linked)
railway link

# Deploy directly
railway up

# Or just redeploy the current code
railway redeploy
```

---

## Method 3: Railway Dashboard (Manual)

You can also trigger a redeploy from the Railway web interface:

1. Go to https://railway.app/dashboard
2. Click on your SONA System project
3. Go to the "Settings" tab
4. Click "Redeploy" button

---

## ⚙️ Important: Environment Variables

When updating, make sure your **environment variables** on Railway are set correctly:

### Required Variables (check in Railway Dashboard → Variables tab):

```bash
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=.railway.app
INSTITUTION_NAME=Nicholls State University  # ← Make sure this is set!
SITE_NAME=Research Participant System
```

### To Update Environment Variables:

1. Go to Railway Dashboard
2. Click on your Django service
3. Go to "Variables" tab
4. Add or edit variables
5. Changes take effect on next deployment

---

## 📋 Update Checklist

Before pushing updates:

- [ ] Test changes locally first
- [ ] Commit all changes with descriptive message
- [ ] Verify `.env` file has correct values (for reference)
- [ ] Check Railway environment variables match your needs
- [ ] Push to GitHub
- [ ] Monitor Railway deployment logs
- [ ] Test the live site after deployment

---

## 🔍 Verify Your Update

After deployment completes:

1. **Check the homepage** - Should show "Nicholls State University"
2. **Check the footer** - Should show "Nicholls State University" (no copyright)
3. **Test protocol submission** - Should work as expected
4. **Check admin panel** - Should be accessible

---

## 🐛 Troubleshooting

### Deployment Failed?

1. **Check Railway logs:**
   - Go to Railway Dashboard → Your Project → Deployments
   - Click on the failed deployment
   - Review error messages

2. **Common issues:**
   - Missing environment variables (especially `INSTITUTION_NAME`)
   - Database migration errors
   - Missing dependencies in `requirements.txt`
   - Port conflicts (Railway handles this automatically)

### Changes Not Showing?

1. **Clear browser cache** - Hard refresh (Cmd+Shift+R on Mac)
2. **Wait a few minutes** - Static files may take time to update
3. **Check Railway logs** - Ensure deployment completed successfully
4. **Verify environment variables** - Make sure `INSTITUTION_NAME` is set on Railway

---

## 📝 Quick Reference

**Most common workflow:**
```bash
# 1. Make changes locally
# 2. Test locally (http://localhost:8001)
# 3. Commit and push
git add -A
git commit -m "Description of changes"
git push

# 4. Wait 2-3 minutes for Railway to redeploy
# 5. Check your live site!
```

---

## 🔗 Useful Links

- **Railway Dashboard:** https://railway.app/dashboard
- **Railway Docs:** https://docs.railway.app
- **Railway CLI Docs:** https://docs.railway.app/develop/cli

---

**Note:** The system automatically runs migrations and collects static files on each deployment, so you don't need to do that manually!
