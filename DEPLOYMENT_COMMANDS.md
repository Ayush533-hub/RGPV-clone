# Deployment Commands Reference

Quick reference for deploying RGPV Flask Application to production.

## 🔧 Initial Setup

### 1. Clone Repository
```bash
git clone https://github.com/Ayush533-hub/RGPV-clone.git
cd RGPV-clone
```

### 2. Create Virtual Environment
```bash
# On Linux/Mac
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Setup Script
```bash
# Generate all necessary files and check configuration
python setup.py --full-setup

# Or manually:
# - Copy .env.example to .env
# - Edit .env with your production values
# - Create necessary directories
```

### 5. Generate SECRET_KEY
```bash
python setup.py --generate-key
# Add the output to your .env file as SECRET_KEY=...

# Or generate manually:
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🚀 Running the Application

### Development (Local Testing)
```bash
# With Flask development server
flask run

# Or
python app.py
```

### Production with Gunicorn (Linux/Mac)

#### Simple Start
```bash
gunicorn app:app
```

#### Production-Ready Setup
```bash
# Using configuration file
gunicorn -c gunicorn_config.py app:app

# Or with inline parameters
gunicorn \
  --workers 4 \
  --worker-class sync \
  --bind 0.0.0.0:8000 \
  --timeout 30 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  --log-level info \
  app:app
```

#### Advanced: With Environment Variables
```bash
export WORKERS=4
export HOST=0.0.0.0
export PORT=8000
export TIMEOUT=30

gunicorn \
  --workers $WORKERS \
  --bind $HOST:$PORT \
  --timeout $TIMEOUT \
  app:app
```

#### With Auto-Reload During Development
```bash
gunicorn \
  --reload \
  --workers 1 \
  --bind 127.0.0.1:8000 \
  app:app
```

### Production with Waitress (Windows-Friendly)

#### Simple Start
```bash
waitress-serve app:app
```

#### Production Setup
```bash
waitress-serve \
  --port=8000 \
  --threads=4 \
  --channel-timeout=30 \
  --log-socket \
  app:app
```

---

## 🔒 Production Deployment Steps

### 1. Pre-Deployment Checklist
```bash
# Check Python version
python --version  # Must be 3.8+

# Verify virtual environment
which python  # Linux/Mac (should show venv path)

# Test database
python -c "from app import init_db; init_db(); print('DB OK')"

# Verify static files
ls StudentInfoPage.html result.html index.html

# Check configuration
python -c "from config import get_config; get_config('production')"
```

### 2. Environment Setup
```bash
# Create .env from template
cp .env.example .env

# Edit with production values
nano .env
# Set:
# FLASK_ENV=production
# FLASK_DEBUG=False
# SECRET_KEY=<generated-key>
# ALLOWED_HOSTS=your-domain.com
# DATABASE_URL=<production-db>
```

### 3. Database Setup
```bash
# Initialize database
python -c "from app import init_db; init_db()"

# Verify database
sqlite3 data/data.db ".tables"  # Should show: marksheets
```

### 4. Start Application

#### Option A: Direct Gunicorn
```bash
cd /path/to/RGPV-clone
source venv/bin/activate
gunicorn -c gunicorn_config.py app:app
```

#### Option B: Systemd Service (Linux)
```bash
# Create service file
sudo nano /etc/systemd/system/rgpv-app.service
```

Paste:
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
    --bind 0.0.0.0:8000 \
    -c gunicorn_config.py \
    app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable rgpv-app
sudo systemctl start rgpv-app

# Check status
sudo systemctl status rgpv-app

# View logs
sudo journalctl -u rgpv-app -f
```

#### Option C: Supervisor (Process Manager)
```bash
sudo apt-get install supervisor

# Create configuration
sudo nano /etc/supervisor/conf.d/rgpv-app.conf
```

Paste:
```ini
[program:rgpv-app]
command=/home/username/RGPV-clone/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:8000 \
    app:app
directory=/home/username/RGPV-clone
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/rgpv-app.log
```

Then:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start rgpv-app
```

#### Option D: Docker (Advanced)
```bash
# Build Docker image
docker build -t rgpv-app .

# Run container
docker run -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  rgpv-app
```

### 5. Configure Web Server (Nginx)

#### Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/rgpv-app
```

Paste:
```nginx
upstream rgpv_app {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name example.com www.example.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com www.example.com;

    # SSL certificates
    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Logging
    access_log /var/log/nginx/rgpv_access.log;
    error_log /var/log/nginx/rgpv_error.log;

    # Client limits
    client_max_body_size 16M;

    location / {
        proxy_pass http://rgpv_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Static files (if served separately)
    location /static/ {
        alias /home/username/RGPV-clone/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable configuration:
```bash
sudo ln -s /etc/nginx/sites-available/rgpv-app /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

### 6. Set Up SSL with Let's Encrypt
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d example.com -d www.example.com
sudo certbot renew --dry-run  # Test auto-renewal
```

---

## 📊 Monitoring & Maintenance

### View Application Logs
```bash
# Gunicorn logs
tail -f logs/app.log

# Access logs
tail -f logs/access.log

# Error logs
tail -f logs/error.log

# System logs (if using systemd)
sudo journalctl -u rgpv-app -f
```

### Monitor Application Health
```bash
# Health check endpoint
curl http://localhost:8000/health

# Check process
ps aux | grep gunicorn

# Check port
lsof -i :8000  # Linux/Mac
netstat -an | grep 8000  # Windows
```

### Restart Application
```bash
# Graceful restart
sudo systemctl restart rgpv-app

# Or with gunicorn
pkill -HUP gunicorn  # Graceful reload
```

### Database Backup
```bash
# Backup SQLite database
cp data/data.db data/data.db.backup

# With timestamp
cp data/data.db data/data.db.backup.$(date +%Y%m%d_%H%M%S)
```

---

## 🐛 Troubleshooting

### Application won't start
```bash
# Check syntax errors
python -m py_compile app.py

# Check imports
python -c "import app"

# Check configuration
python -c "from config import get_config; get_config('production')"

# Run with verbose logging
gunicorn --log-level debug app:app
```

### Database errors
```bash
# Check database exists
ls -la data/data.db

# Check permissions
chmod 666 data/data.db

# Check disk space
df -h

# Verify database integrity
sqlite3 data/data.db "PRAGMA integrity_check;"
```

### Port already in use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
gunicorn --bind 0.0.0.0:8001 app:app
```

### Permission denied
```bash
# Check ownership
ls -la

# Change ownership
sudo chown -R www-data:www-data /path/to/RGPV-clone

# Check file permissions
chmod 755 app.py
chmod 755 logs/
```

---

## 📝 Deployment Checklist

Before going live:

- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Requirements installed
- [ ] .env file configured
- [ ] SECRET_KEY generated and set
- [ ] Database initialized
- [ ] Static files verified
- [ ] CORS properly configured
- [ ] Error handlers in place
- [ ] Logging configured
- [ ] Tests passing
- [ ] SSL certificate installed
- [ ] Nginx configured
- [ ] Firewall rules configured
- [ ] Backups scheduled
- [ ] Monitoring set up
- [ ] Team trained on deployment

---

## 🚨 Emergency Commands

```bash
# Stop application
sudo systemctl stop rgpv-app

# Restart application
sudo systemctl restart rgpv-app

# View last 50 lines of error log
tail -n 50 logs/error.log

# Clear old log files
find logs -name "*.log.*" -delete

# Force database sync
python -c "from app import init_db; init_db()"

# Restart Nginx
sudo systemctl restart nginx
```

---

**Last Updated**: April 26, 2026  
**Version**: 1.0
