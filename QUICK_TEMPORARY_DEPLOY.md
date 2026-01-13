# ⚡ Quick Temporary Deployment for Research Assistant

**Goal:** Get your SONA system online quickly for your RA to use, while you prepare the campus Linux server.

---

## 🚀 Fastest Option: Render (10 minutes)

**Why Render for temporary use:**
- ✅ **Fastest setup** (~10 minutes)
- ✅ **Free** (no credit card needed)
- ✅ **Auto-deploy from GitHub** (easy updates)
- ✅ **Works immediately** - your RA can use it right away
- ✅ **Easy to migrate later** to campus server

### Quick Steps:

1. **Sign up:** https://render.com (use GitHub login)
2. **Create PostgreSQL** (free tier)
3. **Create Web Service** → Connect your GitHub repo
4. **Copy environment variables** from Railway (or use the guide)
5. **Deploy!** (~5 minutes)

**Full guide:** See `RENDER_DEPLOYMENT_GUIDE.md`

---

## 🏫 Campus Linux Server Setup (For Later)

When you're ready to move to your campus server, I've created a guide: `CAMPUS_SERVER_DEPLOYMENT.md`

**Benefits of campus server:**
- ✅ Full control
- ✅ No hosting costs
- ✅ Always-on (no sleep)
- ✅ University network access
- ✅ Can integrate with campus systems

---

## 📋 What Your RA Needs

Once deployed, share with your RA:

1. **URL:** `https://your-app.onrender.com` (or campus server URL)
2. **Login credentials:**
   - Researcher account (if they need it)
   - Participant account (for testing)
3. **Quick start guide** (what they can do)

---

## 🔄 Migration Path

**Temporary (Now):**
- Render → Quick setup, works immediately

**Permanent (Later):**
- Campus Linux Server → Full control, always-on, integrated

**Migration is easy:**
- Export database from Render
- Import to campus server
- Update DNS/URL
- Done!

---

## ⏱️ Timeline

- **Today:** Deploy to Render (10 min) → RA can start using
- **This week:** Test with RA, gather feedback
- **Next week/month:** Set up campus server, migrate data

---

## 🎯 Recommendation

**For right now:** Use **Render** - it's the fastest way to get your RA access.

**For later:** Use your **campus Linux server** - better long-term solution.

I can help you with either! Just let me know which you prefer.
