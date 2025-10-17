# 🎯 Quick: Share Your SONA Demo

## ⚡ Fastest Method (5 minutes)

### 1. Push to GitHub
```bash
# Create a new repo on GitHub.com first, then:
cd "/Users/ccastille/Documents/GitHub/SONA System"
git remote add origin https://github.com/YOUR_USERNAME/SONA-System.git
git push -u origin main
```

### 2. Deploy to Railway
1. Go to https://railway.app
2. Sign up/Login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your SONA-System repo
5. Click "+ New" → "Database" → "PostgreSQL"
6. Add environment variables:
   - `SECRET_KEY` = make-a-long-random-string
   - `DEBUG` = False
7. Go to Settings → Generate Domain
8. **Done!** Share the URL

---

## 🎁 What They'll Get

Your colleague will see:
- Live SONA system at `https://your-app.railway.app`
- 15 demo users already created
- 1 complete study with real data
- 23 signups (attended, booked, no-shows)
- 12 protocol responses
- Full credit tracking system

**Login Credentials to Share:**
- Researcher: researcher@nicholls.edu / demo123
- Instructor: instructor@nicholls.edu / demo123  
- Student: emily.johnson@my.nicholls.edu / demo123

---

## 📖 Detailed Instructions

See **RAILWAY_DEPLOYMENT_GUIDE.md** for step-by-step screenshots and troubleshooting.

---

## ✅ Ready to Deploy?

Your project is fully prepared:
- ✅ Git initialized and committed
- ✅ .gitignore configured
- ✅ Procfile created (auto-runs migrations + demo data)
- ✅ railway.json configured
- ✅ Settings updated for production
- ✅ Requirements.txt ready

**Just push to GitHub and connect to Railway!** 🚀

