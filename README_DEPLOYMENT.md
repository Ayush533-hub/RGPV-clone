# RGPV Student Result Management System - Production Deployment Guide

**Complete guide to deploy your Flask web application to production with best practices.**

## 📚 Documentation Structure

This package includes comprehensive deployment documentation:

1. **DEPLOYMENT_GUIDE.md** - Complete production best practices (10 sections)
2. **DEPLOYMENT_COMMANDS.md** - Step-by-step deployment commands
3. **app_production.py** - Production-ready Flask app with logging & error handling
4. **config.py** - Configuration management for different environments
5. **gunicorn_config.py** - WSGI server configuration
6. **requirements.txt** - Python dependencies
7. **.env.example** - Environment configuration template
8. **setup.py** - Automated setup script

---

## 🎯 Quick Start (5 Minutes)

### For Development
```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run application
python app.py

# 4. Open browser
# Visit: http://localhost:5000
```

### For Production
```bash
# 1. Setup
python setup.py --full-setup

# 2. Edit .env with production values
nano .env

# 3. Run with Gunicorn
gunicorn -c gunicorn_config.py app:app

# 4. Configure Nginx (see DEPLOYMENT_COMMANDS.md)
```

---

## ⚠️ Critical Security Points

### Never Do This in Production:

```python
# ❌ WRONG
app.run(debug=True)  # Exposes debugger to attackers!
SECRET_KEY = "hardcoded-secret"  # Visible in source code!
CORS(app)  # Allows all origins!
```

### Always Do This:

```python
# ✅ CORRECT
DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"
app.run(debug=DEBUG)
SECRET_KEY = os.getenv("SECRET_KEY")  # From environment
CORS(app, resources={"/*": {"origins": ["example.com"]}})  # Whitelist
```

---

## 📋 10-Point Deployment Checklist

| Item | Development | Production | Status |
|------|:-----------:|:----------:|:------:|
| Debug Mode OFF | ❌ ON | ✅ OFF | - |
| SECRET_KEY | dev-key | generated | - |
| Database | SQLite | PostgreSQL | - |
| WSGI Server | Flask | Gunicorn | - |
| Static Files | direct | url_for() | - |
| Error Handling | basic | comprehensive | - |
| Logging | console | file+console | - |
| CORS | allow all | whitelist | - |
| SSL/HTTPS | no | yes | - |
| Monitoring | no | yes | - |

---

## 🔧 File Structure After Deployment

```
RGPV-clone/
├── app.py                    # Original app (keep for reference)
├── app_production.py         # ✨ NEW: Production version with logging
├── config.py                 # ✨ NEW: Configuration management
├── gunicorn_config.py        # ✨ NEW: WSGI server config
├── setup.py                  # ✨ NEW: Setup automation
│
├── requirements.txt          # ✨ NEW: Python dependencies
├── .env.example             # ✨ NEW: Config template
├── .env                     # ✨ NEW: Production config (not in git!)
├── .gitignore               # ✨ NEW: Prevent committing secrets
│
├── DEPLOYMENT_GUIDE.md      # ✨ NEW: Best practices (10 sections)
├── DEPLOYMENT_COMMANDS.md   # ✨ NEW: Command reference
├── WORKFLOW_GUIDE.md        # Original workflow documentation
│
├── templates/               # ✨ RECOMMENDED: Move HTML here
│   ├── index.html
│   ├── result.html
│   └── student_info.html
│
├── static/                  # ✨ RECOMMENDED: Move static files here
│   ├── css/
│   │   ├── style.css
│   │   └── styles.css
│   ├── js/
│   └── images/
│       └── RGPVlogo.png
│
├── data/                    # ✨ RECOMMENDED: Database folder
│   ├── data.db
│   └── backups/
│
└── logs/                    # ✨ RECOMMENDED: Log files folder
    ├── app.log
    ├── access.log
    └── error.log
```

---

## 🚀 Deployment Methods

### Method 1: Gunicorn + Nginx (Recommended for Linux)
- **Performance**: ⭐⭐⭐⭐⭐ High
- **Setup**: Medium
- **Monitoring**: Excellent
- [See detailed guide →](DEPLOYMENT_COMMANDS.md)

### Method 2: Waitress (Recommended for Windows)
- **Performance**: ⭐⭐⭐⭐ High
- **Setup**: Easy
- **Monitoring**: Good
- [See detailed guide →](DEPLOYMENT_COMMANDS.md)

### Method 3: Docker (Recommended for Scalability)
- **Performance**: ⭐⭐⭐⭐⭐ High
- **Setup**: Hard
- **Monitoring**: Excellent
- [See detailed guide →](DEPLOYMENT_COMMANDS.md)

### Method 4: Platform as a Service (Heroku/PythonAnywhere)
- **Performance**: ⭐⭐⭐ Medium
- **Setup**: Easy
- **Monitoring**: Built-in
- [See detailed guide →](DEPLOYMENT_COMMANDS.md)

---

## 📖 Key Documentation

### 1. Production Best Practices
**Read**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

Topics covered:
- Debug mode security risks
- Project structure best practices
- Static files with url_for()
- Requirements.txt management
- Environment variables
- Host & port configuration
- WSGI server setup (Gunicorn/Waitress)
- Error handling
- 10 common deployment mistakes

### 2. Step-by-Step Commands
**Read**: [DEPLOYMENT_COMMANDS.md](DEPLOYMENT_COMMANDS.md)

Includes:
- Initial setup commands
- Gunicorn production setup
- Waitress setup (Windows)
- Systemd service configuration
- Nginx configuration with SSL
- Let's Encrypt SSL setup
- Monitoring commands
- Troubleshooting guide

### 3. Your Application Logic
**Read**: [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md)

Explains:
- StudentInfoPage → Search enrollment
- result.html → Edit/save results
- Database operations
- Complete workflow

---

## 🔐 Security Best Practices

### 1. Environment Variables
```bash
# ✅ DO: Use .env for secrets
DATABASE_PASSWORD=$(cat .env | grep DB_PASSWORD)

# ❌ DON'T: Hardcode secrets
password = "super_secret_123"
```

### 2. CORS Configuration
```python
# ✅ DO: Whitelist specific origins
CORS(app, resources={
    r"/*": {"origins": ["https://example.com"]}
})

# ❌ DON'T: Allow all origins
CORS(app)
```

### 3. Input Validation
```python
# ✅ DO: Validate all input
if not enrollment or not enrollment.isalnum():
    return error, 400

# ❌ DON'T: Trust user input
c.execute(f"SELECT * FROM users WHERE id={user_id}")
```

### 4. Debug Mode
```python
# ✅ DO: Disable in production
DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"

# ❌ DON'T: Run with debug=True
app.run(debug=True)
```

### 5. SSL/HTTPS
```bash
# ✅ DO: Use HTTPS in production
https://example.com/api

# ❌ DON'T: Use HTTP
http://example.com/api
```

---

## 🛠️ Automated Setup

The `setup.py` script handles common setup tasks:

```bash
# Full setup
python setup.py --full-setup

# Generate SECRET_KEY
python setup.py --generate-key

# Check all requirements
python setup.py --check-all

# Install dependencies only
python setup.py --install-deps
```

---

## 📊 Performance Comparison

| Aspect | Flask Dev | Gunicorn | Waitress | Docker |
|--------|:---------:|:--------:|:--------:|:------:|
| Requests/sec | ~100 | ~1000 | ~800 | ~1000 |
| Concurrent Users | ~10 | ~500 | ~400 | ~500 |
| Memory Usage | Low | Medium | Medium | Higher |
| Setup Time | 1 min | 5 min | 5 min | 20 min |
| Monitoring | None | Good | Good | Excellent |

---

## 🚨 Common Issues & Fixes

### Issue 1: "Port already in use"
```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>

# Or use different port
gunicorn --bind 0.0.0.0:8001 app:app
```

### Issue 2: "Permission denied" on database
```bash
# Fix file permissions
chmod 666 data/data.db
chmod 755 data/
```

### Issue 3: ".env not loaded"
```bash
# Verify .env exists
ls -la .env

# Check it's readable
cat .env

# Restart application
sudo systemctl restart rgpv-app
```

### Issue 4: "Static files not found"
```bash
# Make sure using url_for() in templates
<img src="{{ url_for('static', filename='images/RGPVlogo.png') }}" />

# Not direct paths
# <img src="RGPVlogo.png" />  ❌ WRONG
```

### Issue 5: "Database locked"
```bash
# SQLite issue with multiple workers
# Solution 1: Use fewer workers
gunicorn --workers 1 app:app

# Solution 2: Use PostgreSQL
# Update DATABASE_URL in .env
```

---

## 📚 Next Steps

### Step 1: Read Documentation
- [ ] Read [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) (30 mins)
- [ ] Read [DEPLOYMENT_COMMANDS.md](DEPLOYMENT_COMMANDS.md) (15 mins)

### Step 2: Prepare Environment
- [ ] Run `python setup.py --full-setup`
- [ ] Generate SECRET_KEY: `python setup.py --generate-key`
- [ ] Edit `.env` with production values

### Step 3: Test Locally
- [ ] Install requirements: `pip install -r requirements.txt`
- [ ] Run development server: `python app.py`
- [ ] Test all features work

### Step 4: Setup WSGI Server
- **Linux**: Use Gunicorn (see commands)
- **Windows**: Use Waitress (see commands)
- **Both**: Use Docker (see commands)

### Step 5: Configure Web Server
- [ ] Setup Nginx (for Linux)
- [ ] Configure SSL with Let's Encrypt
- [ ] Setup backup & monitoring

### Step 6: Deploy
- [ ] Backup database
- [ ] Deploy code to production server
- [ ] Run database migrations
- [ ] Start application
- [ ] Verify health endpoint

### Step 7: Monitor
- [ ] Check logs daily
- [ ] Monitor resource usage
- [ ] Track errors
- [ ] Schedule backups

---

## 📞 Getting Help

### Documentation
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Best practices
- [DEPLOYMENT_COMMANDS.md](DEPLOYMENT_COMMANDS.md) - Commands
- [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) - Application logic

### External Resources
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)

### Community
- Stack Overflow: `[flask] [deployment]`
- Flask Community: https://flask.palletsprojects.com/support/
- GitHub Issues: Ask in repository

---

## ✅ Deployment Verification

After deployment, verify:

```bash
# 1. Health check
curl http://your-domain.com/health

# 2. Check logs
tail -f logs/app.log

# 3. Test enrollment lookup
curl http://your-domain.com/check?enrollment=12345

# 4. Check SSL certificate
curl -I https://your-domain.com

# 5. Monitor resources
ps aux | grep gunicorn
```

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-04-26 | Initial release with complete deployment guide |

---

## 📄 License

This deployment guide is provided as-is for the RGPV Student Result Management System.

---

**Last Updated**: April 26, 2026  
**Status**: ✅ Production Ready  
**Maintainer**: RGPV Project Team

---

**Happy Deploying! 🚀**
