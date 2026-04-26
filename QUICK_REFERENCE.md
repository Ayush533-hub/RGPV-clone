# Production Deployment Quick Reference Card

## 🚀 5-Minute Quick Start

### Setup
```bash
python setup.py --full-setup      # Automated setup
```

### Configure
```bash
nano .env                          # Edit configuration
# Set: FLASK_DEBUG=False, SECRET_KEY, ALLOWED_HOSTS
```

### Run
```bash
# Option 1: Development
python app.py

# Option 2: Production
gunicorn -c gunicorn_config.py app:app

# Option 3: Docker
docker-compose up -d
```

---

## 🔑 Essential Commands

| Command | Purpose |
|---------|---------|
| `python setup.py --full-setup` | Complete automated setup |
| `python setup.py --generate-key` | Generate SECRET_KEY |
| `python setup.py --check-all` | Verify configuration |
| `pip install -r requirements.txt` | Install dependencies |
| `gunicorn -c gunicorn_config.py app:app` | Start Gunicorn |
| `curl http://localhost:5000/health` | Health check |
| `tail -f logs/app.log` | View logs in real-time |
| `docker-compose up -d` | Start with Docker |
| `docker-compose logs -f` | Docker logs |

---

## 🔐 Security Essentials

| Item | ✅ DO | ❌ DON'T |
|------|------|---------|
| Debug Mode | `FLASK_DEBUG=False` | `debug=True` |
| SECRET_KEY | From `.env` | Hardcoded value |
| CORS | Whitelist origins | `CORS(app)` |
| Input | Validate all | Trust user input |
| Passwords | Encrypted, hashed | Plain text |

---

## 📋 Pre-Deployment Checklist

- [ ] `FLASK_DEBUG=False`
- [ ] `SECRET_KEY` generated
- [ ] `.env` not in git
- [ ] Database tested
- [ ] Static files working
- [ ] Error handlers present
- [ ] Logging configured
- [ ] CORS whitelist set
- [ ] SSL/HTTPS ready
- [ ] Firewall configured

---

## 🗂️ Key Files

| File | Purpose | Action |
|------|---------|--------|
| `requirements.txt` | Dependencies | Install |
| `.env` | Secrets | Configure |
| `app_production.py` | Main app | Deploy |
| `gunicorn_config.py` | Server | Run |
| `config.py` | Settings | Import |
| `DEPLOYMENT_GUIDE.md` | Details | Read |
| `DEPLOYMENT_COMMANDS.md` | Steps | Follow |

---

## 🔧 Deployment Methods

### Gunicorn (Linux/Mac)
```bash
gunicorn --workers 4 --bind 0.0.0.0:8000 app:app
```

### Waitress (Windows)
```bash
waitress-serve --port=8000 --threads=4 app:app
```

### Docker (All)
```bash
docker-compose up -d
```

### Systemd (Linux)
```bash
sudo systemctl start rgpv-app
```

---

## 🐛 Quick Fixes

| Problem | Fix |
|---------|-----|
| Port in use | `kill -9 $(lsof -t -i :8000)` |
| Permission error | `chmod 666 data/data.db` |
| .env not loaded | Check file exists: `ls -la .env` |
| No static files | Use `url_for('static', ...)` |
| Database locked | Use 1 worker: `--workers 1` |

---

## 📊 Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Requests/sec | 500+ | With Gunicorn |
| Response time | <100ms | Typical |
| Concurrent users | 200+ | At capacity |
| Memory usage | <500MB | With 4 workers |
| CPU usage | 50-70% | Healthy |

---

## 📞 Documentation Map

```
START HERE
    ↓
README_DEPLOYMENT.md (Overview)
    ↓
SETUP_INSTRUCTIONS.md (This checklist)
    ↓
DEPLOYMENT_GUIDE.md (Detailed guide)
    ↓
DEPLOYMENT_COMMANDS.md (Exact commands)
    ↓
Specific sections as needed
```

---

## 🆘 Emergency Commands

```bash
# Stop app
sudo systemctl stop rgpv-app

# Restart app  
sudo systemctl restart rgpv-app

# View errors
tail -100 logs/error.log

# Check health
curl http://localhost:5000/health

# Force database sync
python -c "from app import init_db; init_db()"

# View running process
ps aux | grep gunicorn
```

---

## 💡 Best Practices

1. **Always use environment variables** - Never hardcode secrets
2. **Enable HTTPS** - Encrypt all traffic
3. **Monitor logs** - Track errors immediately
4. **Backup database** - Automate daily backups
5. **Use load balancer** - Distribute traffic
6. **Monitor resources** - CPU, memory, disk
7. **Update dependencies** - Security patches
8. **Test before deploy** - Always verify locally
9. **Document changes** - Keep runbooks updated
10. **Plan for failure** - Have rollback strategy

---

## 🚨 Critical Settings

```python
# In .env
FLASK_ENV=production          # ← MUST be production
FLASK_DEBUG=False             # ← MUST be False
SECRET_KEY=<generated-key>    # ← MUST change from example
ALLOWED_HOSTS=your-domain.com # ← MUST specify
DATABASE_URL=<production-db>  # ← MUST be different from dev
```

---

## ⏱️ Estimated Times

| Task | Time |
|------|------|
| Read guides | 1-2 hours |
| Run setup | 5 minutes |
| Configure .env | 5 minutes |
| Deploy to production | 15-30 minutes |
| Setup monitoring | 30 minutes |
| Total (first time) | 2-3 hours |

---

## 📞 Need Help?

1. **Check DEPLOYMENT_GUIDE.md** - Section on your issue
2. **Check DEPLOYMENT_COMMANDS.md** - Troubleshooting section
3. **Search logs** - Look for error messages
4. **Review config** - Verify .env settings
5. **Test health** - `curl http://localhost:5000/health`

---

## ✅ Post-Deployment

```bash
# Verify running
ps aux | grep gunicorn

# Test endpoint
curl https://your-domain.com/health

# Check logs
tail -f logs/app.log

# Monitor resources
watch -n 1 'ps aux | grep gunicorn'
```

---

**Bookmark this page for quick reference!**

Last Updated: April 26, 2026
