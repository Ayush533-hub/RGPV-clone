# 🚀 RENDER DEPLOYMENT - QUICK START

## ✅ Pre-Deployment Checklist

- ✅ Code pushed to GitHub
- ✅ render.yaml configuration file created
- ✅ requirements.txt with all dependencies
- ✅ app_production.py or app.py ready
- ✅ .env.example file created
- ✅ .gitignore prevents .env commits

**All ready!** Now deploy!

---

## 🎯 5-MINUTE DEPLOYMENT

### **Step 1: Go to Render.com**
Open: https://dashboard.render.com

### **Step 2: Sign In with GitHub**
- Click **Sign Up** or **Sign In**
- Choose **GitHub**
- Click **Authorize Render**

### **Step 3: Create New Web Service**
1. Click **New +** (top right)
2. Select **Web Service**
3. Click **Deploy from GitHub**
4. Search for **RGPV-clone**
5. Click **Connect**

### **Step 4: Configure Service**

Fill in these fields:

| Field | Value |
|-------|-------|
| **Name** | `rgpv-app` |
| **Region** | Keep default |
| **Branch** | `main` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn -c gunicorn_config.py app:app` |
| **Instance** | Free (or Starter $7) |

### **Step 5: Add Environment Variables**

Click **Environment** and add:

```
FLASK_ENV=production
FLASK_DEBUG=False
HOST=0.0.0.0
PORT=5000
SECRET_KEY=<click generate button>
```

### **Step 6: Deploy!**

Click **Create Web Service** (blue button)

Wait 2-3 minutes... ⏳

Done! 🎉 You'll get a URL like:
```
https://rgpv-app.onrender.com
```

---

## ✅ Verify It Works

Test these:

```bash
# Test 1: Visit your app
https://rgpv-app.onrender.com

# Test 2: Check health
https://rgpv-app.onrender.com/health

# Test 3: Try enrollment search
https://rgpv-app.onrender.com/
# (Enter an enrollment number)
```

---

## 🔄 Future Updates

Every time you push to GitHub:

```bash
git add .
git commit -m "Your message"
git push origin main
```

**Render will auto-deploy within 2 minutes!**

---

## 🆘 If Something Goes Wrong

1. Check Render dashboard **Logs** tab
2. Look for error messages
3. Check [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) troubleshooting section
4. Or run locally first: `gunicorn -c gunicorn_config.py app:app`

---

**That's it! Your app is LIVE!** 🚀

For detailed guide, see: [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)
