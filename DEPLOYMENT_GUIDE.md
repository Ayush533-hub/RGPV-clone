# Flask Production Deployment Guide

Complete checklist and best practices for deploying your Flask RGPV application to production.

---

## 📋 Table of Contents
1. [Debug Mode & Security](#1-debug-mode--security)
2. [Project Structure](#2-project-structure)
3. [Static Files Handling](#3-static-files-handling)
4. [Requirements.txt](#4-requirementstxt)
5. [Environment Variables](#5-environment-variables)
6. [Host & Port Configuration](#6-host--port-configuration)
7. [WSGI Server Setup](#7-wsgi-server-setup)
8. [Error Handling](#8-error-handling)
9. [Deployment Checklist](#9-deployment-checklist)
10. [Common Mistakes](#10-common-mistakes)

---

## 1. Debug Mode & Security

### ❌ **Why Debug Mode is DANGEROUS in Production:**

```python
# WRONG - NEVER DO THIS IN PRODUCTION
if __name__ == "__main__":
    app.run(debug=True)  # ⚠️ SECURITY RISK!
```

**Risks of `debug=True`:**
- **Debugger Console Exposed**: Anyone can access interactive Python shell on your server
- **Code Visibility**: Full source code visible in error pages
- **Auto Reload**: App restarts on file changes, causing downtime
- **Security PIN**: Debugger PIN can be bruteforced
- **Performance**: Slower execution with debugging overhead

### ✅ **Correct Production Setup:**

```python
# CORRECT - Production ready
if __name__ == "__main__":
    # Debug mode controlled by environment variable
    DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"
    app.run(
        host='0.0.0.0',
        port=int(os.getenv("PORT", 5000)),
        debug=DEBUG  # False in production
    )
```

---

## 2. Project Structure

### **Recommended Directory Layout:**

```
RGPV-clone/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (DON'T commit!)
├── .env.example                # Template for .env (commit this!)
├── .gitignore                  # Git ignore file
├── runtime.txt                 # Python version for Heroku
│
├── templates/                  # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── result.html
│   └── student_info.html
│
├── static/                     # Static files (CSS, JS, images)
│   ├── css/
│   │   ├── style.css
│   │   └── responsive.css
│   ├── js/
│   │   └── main.js
│   └── images/
│       └── RGPVlogo.png
│
├── data/                       # Database files
│   └── data.db
│
└── utils/                      # Helper functions
    ├── __init__.py
    └── database.py
```

### **Why This Structure Matters:**

| Component | Why | Benefit |
|-----------|-----|---------|
| `templates/` | Separate presentation layer | Easier maintenance & security |
| `static/` | Cached by browser & CDN | Better performance |
| `config.py` | Centralized settings | Easy environment switching |
| `.env` | Secrets management | Security best practice |
| `utils/` | Reusable functions | DRY principle |

---

## 3. Static Files Handling

### ❌ **Wrong: Direct file paths**
```python
# WRONG - Hardcoded path
<img src="RGPVlogo.png" />
<link rel="stylesheet" href="style.css" />
```

### ✅ **Correct: Using `url_for()`**

```python
# In your HTML/template
<img src="{{ url_for('static', filename='images/RGPVlogo.png') }}" />
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}" />
<script src="{{ url_for('static', filename='js/main.js') }}"></script>
```

### **Benefits:**
- ✅ Works in development AND production
- ✅ CDN-friendly (easy to change static file serving)
- ✅ Automatic cache busting (add `?v=1.0.0`)
- ✅ Works with different URL prefixes

---

## 4. Requirements.txt

### **Generate from your environment:**

```bash
pip freeze > requirements.txt
```

### **Minimal requirements.txt for this project:**

```text
Flask==2.3.2
Flask-CORS==4.0.0
python-dotenv==1.0.0
gunicorn==21.2.0
Werkzeug==2.3.6
```

### **Better: Pinned versions (production-safe):**

```text
# Web Framework
Flask==2.3.2
Flask-CORS==4.0.0
Werkzeug==2.3.6

# Environment & Configuration
python-dotenv==1.0.0

# Production WSGI Server
gunicorn==21.2.0
# OR use Waitress as alternative
# waitress==2.1.2

# Optional but recommended
python-dateutil==2.8.2
```

### **Install from requirements.txt:**

```bash
pip install -r requirements.txt
```

---

## 5. Environment Variables

### **❌ Wrong: Hardcoded secrets**
```python
SECRET_KEY = "mysecretkey123"
DATABASE_URL = "postgresql://user:password@localhost/db"
API_KEY = "sk-12345678"
```

### **✅ Correct: Use environment variables**

```python
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-dev-key")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data.db")
DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
```

### **.env.example (COMMIT THIS)**
```
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=False
FLASK_APP=app.py

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production

# Database
DATABASE_URL=sqlite:///data.db
DB_BACKUP_PATH=/backups

# Server
HOST=0.0.0.0
PORT=5000
ALLOWED_HOSTS=localhost,127.0.0.1,example.com

# API Keys (if any)
API_KEY=your-api-key-here
```

### **.env (DON'T COMMIT THIS)**
```
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=prod-secret-xyz-change-this-randomly
DATABASE_URL=postgresql://user:password@db.example.com/rgpv_prod
PORT=8000
ALLOWED_HOSTS=www.example.com,example.com
```

### **.gitignore**
```
# Environment variables
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Database
*.db
*.sqlite
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Temp files
*.tmp
temp/
```

---

## 6. Host & Port Configuration

### **Development vs Production:**

```python
# Development (localhost only)
app.run(host='127.0.0.1', port=5000)

# Production (accessible from outside)
app.run(host='0.0.0.0', port=8000)
```

### **Explanation:**
- **127.0.0.1**: Only local machine can access (default)
- **0.0.0.0**: All network interfaces (needed for server)
- **Port**: Use 8000+ for non-root, avoid 5000 (Flask default)

### **Configuration in app.py:**

```python
if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")  # Dev: localhost, Prod: 0.0.0.0
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "False") == "True"
    
    app.run(host=host, port=port, debug=debug)
```

---

## 7. WSGI Server Setup

### **Why Not Use Flask's Built-in Server:**

| Feature | Flask Dev | Gunicorn | Waitress |
|---------|-----------|----------|----------|
| Performance | ⭐ Low | ⭐⭐⭐⭐⭐ High | ⭐⭐⭐⭐ High |
| Concurrency | ❌ Single | ✅ Multi-worker | ✅ Multi-threaded |
| Production Ready | ❌ No | ✅ Yes | ✅ Yes |
| Error Handling | ❌ Poor | ✅ Excellent | ✅ Good |
| Stability | ❌ Crashes | ✅ Robust | ✅ Robust |

### **Option 1: Gunicorn (Recommended for Linux/Mac)**

**Installation:**
```bash
pip install gunicorn
```

**Run:**
```bash
# Single worker (testing)
gunicorn app:app

# Multiple workers (production)
gunicorn --workers 4 --bind 0.0.0.0:8000 app:app

# With timeout & graceful restart
gunicorn \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --timeout 30 \
  --access-logfile - \
  app:app
```

**With .env:**
```bash
gunicorn \
  --workers $(python -c "import multiprocessing; print(multiprocessing.cpu_count() * 2 + 1)") \
  --bind $HOST:$PORT \
  --timeout 30 \
  app:app
```

### **Option 2: Waitress (Windows-Friendly)**

**Installation:**
```bash
pip install waitress
```

**Run:**
```bash
# Simple
waitress-serve --port=8000 app:app

# With multiple threads
waitress-serve --port=8000 --threads=4 app:app

# Production setup
waitress-serve \
  --port=8000 \
  --threads=4 \
  --channel-timeout=30 \
  app:app
```

### **Systemd Service (Linux)**

**Create `/etc/systemd/system/rgpv-app.service`:**

```ini
[Unit]
Description=RGPV Flask Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/home/username/RGPV-clone
Environment="PATH=/home/username/RGPV-clone/venv/bin"
EnvironmentFile=/home/username/RGPV-clone/.env
ExecStart=/home/username/RGPV-clone/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:8000 \
    --timeout 30 \
    app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable & Start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable rgpv-app
sudo systemctl start rgpv-app
sudo systemctl status rgpv-app
```

---

## 8. Error Handling

### **Basic Error Handlers:**

```python
from flask import render_template

# 404 - Not Found
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

# 500 - Server Error
@app.errorhandler(500)
def server_error(error):
    # Log the error (implement proper logging)
    print(f"Server Error: {error}")
    return jsonify({"error": "Internal server error"}), 500

# 403 - Forbidden
@app.errorhandler(403)
def forbidden(error):
    return jsonify({"error": "Forbidden"}), 403

# 400 - Bad Request
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request"}), 400
```

### **Logging (CRITICAL for production):**

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Use it
@app.route("/check")
def check_enrollment():
    try:
        enrollment = request.args.get("enrollment")
        logger.info(f"Checking enrollment: {enrollment}")
        # Your code here
    except Exception as e:
        logger.error(f"Error checking enrollment: {str(e)}")
        return jsonify({"error": "Database error"}), 500
```

---

## 9. Deployment Checklist

### **Before Deployment:**

- [ ] **Debug Mode OFF**: `FLASK_DEBUG=False`
- [ ] **SECRET_KEY Set**: Generated unique secret key
- [ ] **CORS Configured**: Not allowing all origins
- [ ] **Requirements.txt**: All dependencies listed
- [ ] **Database**: Migrations tested
- [ ] **Static Files**: All paths use `url_for()`
- [ ] **Error Handlers**: Custom 404, 500 handlers
- [ ] **Logging**: Configured with file rotation
- [ ] **Environment Variables**: `.env` not committed
- [ ] **Tests Passing**: Run your test suite
- [ ] **SSL/HTTPS**: Certificate configured
- [ ] **Backups**: Database backup strategy
- [ ] **Monitoring**: Error tracking (Sentry, etc.)
- [ ] **Rate Limiting**: Prevent abuse
- [ ] **CORS Headers**: Proper origin whitelist

### **Deployment Commands:**

```bash
# 1. Clone/Pull code
git clone https://github.com/Ayush533-hub/RGPV-clone.git
cd RGPV-clone

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
cp .env.example .env
# Edit .env with production values
nano .env

# 5. Initialize database
python -c "from app import init_db; init_db()"

# 6. Start with WSGI server
gunicorn --workers 4 --bind 0.0.0.0:8000 app:app
```

---

## 10. Common Mistakes

### **Mistake 1: Using Flask's Development Server in Production**
```python
# ❌ WRONG
app.run()  # Uses Flask's single-threaded server

# ✅ CORRECT
# Use gunicorn/waitress instead
```

### **Mistake 2: Hardcoding Database Paths**
```python
# ❌ WRONG
DB_NAME = "C:\\Users\\Ayush\\data.db"  # Won't work on server!

# ✅ CORRECT
DB_NAME = os.getenv("DATABASE_URL", "data.db")
```

### **Mistake 3: Serving Static Files with Flask**
```python
# ❌ WRONG - Slow in production
@app.route("/<filename>")
def serve_file(filename):
    return send_file(filename)

# ✅ CORRECT - Let web server handle static files
# Use nginx or configure Flask static folder properly
```

### **Mistake 4: Committing .env File**
```bash
# ❌ WRONG
git add .env
git commit -m "Added environment"

# ✅ CORRECT
# Add .env to .gitignore
# Commit .env.example instead
echo ".env" >> .gitignore
```

### **Mistake 5: No Error Handling**
```python
# ❌ WRONG - App crashes on error
@app.route("/check")
def check():
    data = request.json  # Crashes if JSON is invalid!

# ✅ CORRECT
@app.route("/check")
def check():
    try:
        data = request.json or {}
        enrollment = data.get("enrollment")
        if not enrollment:
            return jsonify({"error": "Missing enrollment"}), 400
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": "Server error"}), 500
```

### **Mistake 6: Using SQLite in Multi-Process Environment**
```python
# ❌ PROBLEMATIC - SQLite not ideal for multiple Gunicorn workers
# Can cause database locks and corruption

# ✅ BETTER - Use PostgreSQL for production
DATABASE_URL = "postgresql://user:password@db.example.com/rgpv_prod"
```

### **Mistake 7: No HTTPS**
```python
# ❌ WRONG - Sending data over HTTP is insecure

# ✅ CORRECT - Use HTTPS with certificate
# Configure nginx or use Let's Encrypt
```

### **Mistake 8: CORS Too Permissive**
```python
# ❌ WRONG - Anyone can access your API
CORS(app)  # Allows all origins!

# ✅ CORRECT - Whitelist specific domains
CORS(app, resources={
    r"/*": {
        "origins": ["https://example.com", "https://www.example.com"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})
```

### **Mistake 9: No Logging**
```python
# ❌ WRONG - Silent failures
@app.route("/save", methods=["POST"])
def save():
    # Something fails...nobody knows

# ✅ CORRECT - Log everything
@app.route("/save", methods=["POST"])
def save():
    logger.info(f"Save request received: {request.remote_addr}")
    try:
        # Your code
        logger.info("Data saved successfully")
    except Exception as e:
        logger.error(f"Save failed: {e}")
```

### **Mistake 10: Not Testing Before Deployment**
```bash
# ✅ CORRECT - Always test locally first
export FLASK_ENV=production
export FLASK_DEBUG=False
gunicorn --workers 1 --bind 127.0.0.1:8000 app:app

# Then test:
curl http://127.0.0.1:8000/
```

---

## 🚀 Quick Start: From Development to Production

### **Step 1: Local Testing**
```bash
pip install -r requirements.txt
python app.py  # Test locally
```

### **Step 2: Prepare for Production**
```bash
# Create .env
cp .env.example .env
# Edit .env with production values
nano .env

# Create logs directory
mkdir -p logs
```

### **Step 3: Deploy**
```bash
# On your production server
gunicorn --workers 4 --bind 0.0.0.0:8000 --timeout 30 app:app
```

### **Step 4: Monitor**
```bash
# Check logs
tail -f logs/app.log

# Monitor process
ps aux | grep gunicorn
```

---

## 📚 Additional Resources

- [Flask Production Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Python-dotenv](https://github.com/thripwire/python-dotenv)
- [12 Factor App](https://12factor.net/)
- [OWASP Security Guidelines](https://owasp.org/)

---

**Last Updated**: April 26, 2026  
**Version**: 1.0
