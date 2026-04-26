# 📋 POSTGRESQL MIGRATION CHECKLIST

## Quick Start (Choose Your Path)

### Path 1️⃣: Local Development (Windows/Mac)
- [ ] Install PostgreSQL from postgresql.org
- [ ] Create database: `createdb rgpv_db`
- [ ] Create user: `psql -U postgres` (then SQL commands)
- [ ] Copy env file: `cp .env.postgresql .env`
- [ ] Edit .env with your PostgreSQL password
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Initialize tables: `flask db-init`
- [ ] Test locally: `python app_sqlalchemy.py`

### Path 2️⃣: Docker (Windows/Mac/Linux)
- [ ] Install Docker Desktop
- [ ] Run container: `docker run --name rgpv_postgres -e POSTGRES_PASSWORD=... -p 5432:5432 -d postgres:15`
- [ ] Copy env file: `cp .env.postgresql .env`
- [ ] Edit .env: `DATABASE_URL=postgresql://postgres:password@localhost:5432/postgres`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Initialize: `flask db-init`
- [ ] Run app: `python app_sqlalchemy.py`

### Path 3️⃣: Production (Render.com - Auto Setup)
- [ ] Push code to GitHub with new files
- [ ] Render creates PostgreSQL automatically ✨
- [ ] DATABASE_URL is set automatically
- [ ] Just deploy! ✅

---

## Files Created

### New Application Files
- ✅ **models.py** - Database models (StudentMarksheet, StudentProfile, AuditLog)
- ✅ **app_sqlalchemy.py** - New Flask app using SQLAlchemy
- ✅ **POSTGRESQL_SETUP_GUIDE.md** - Detailed setup guide

### Updated Files
- ✅ **requirements.txt** - Added SQLAlchemy, psycopg2
- ✅ **.env.postgresql** - PostgreSQL configuration template

### Environment Files
- 📝 **.env.example** - Keep using this for reference
- 📝 **.env** - Your local configuration (create from .env.postgresql)

---

## Installation Steps

### Step 1: Install PostgreSQL
```bash
# Windows:
# Download from: https://www.postgresql.org/download/windows/
# Or: choco install postgresql

# macOS:
# brew install postgresql@15
# brew services start postgresql@15

# Linux (Ubuntu):
# sudo apt update && sudo apt install postgresql

# Docker:
# docker run -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15
```

### Step 2: Create Database
```bash
# Windows/macOS
psql -U postgres

# Then run in SQL:
CREATE DATABASE rgpv_db;
CREATE USER rgpv_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE rgpv_db TO rgpv_user;
\q

# Linux
sudo -u postgres psql
CREATE DATABASE rgpv_db;
CREATE USER rgpv_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE rgpv_db TO rgpv_user;
\q
```

### Step 3: Configure App
```bash
# Copy environment file
cp .env.postgresql .env

# Edit .env - change these:
# DATABASE_URL=postgresql://rgpv_user:YOUR_PASSWORD@localhost:5432/rgpv_db
# SECRET_KEY=generate_a_random_key
# FLASK_DEBUG=True (for development only)
nano .env
```

### Step 4: Install Python Packages
```bash
# Activate virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 5: Initialize Database
```bash
# Create tables
python -c "from app_sqlalchemy import app, db; db.create_all()"

# Or using Flask CLI
flask db-init

# Verify tables exist
psql -U rgpv_user -d rgpv_db -c "\dt"
```

### Step 6: Add Sample Data
```bash
# Flask CLI
flask seed-data

# Or manually
python -c "from models import seed_sample_data; from app_sqlalchemy import app; seed_sample_data(app)"
```

### Step 7: Run Application
```bash
# Development
python app_sqlalchemy.py

# Open browser
# http://localhost:5000
```

---

## Migration From SQLite

### Backup SQLite Data
```bash
# Backup original
cp app.db app.db.backup

# Export to JSON
python -c "
import sqlite3, json
conn = sqlite3.connect('app.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute('SELECT * FROM marksheets')
rows = cursor.fetchall()
with open('data_backup.json', 'w') as f:
    json.dump([dict(row) for row in rows], f)
conn.close()
print('Exported to data_backup.json')
"
```

### Import to PostgreSQL
```python
# Save as: import_data.py
import json
from models import db, StudentMarksheet
from app_sqlalchemy import app

with app.app_context():
    with open('data_backup.json', 'r') as f:
        records = json.load(f)
    
    for record in records:
        student = StudentMarksheet(
            enrollment=record['enrollment'],
            name=record.get('name', 'Unknown'),
            data=json.loads(record['data']) if isinstance(record.get('data'), str) else record.get('data')
        )
        db.session.add(student)
    
    db.session.commit()
    print(f"✅ Imported {len(records)} records!")

# Run it
# python import_data.py
```

---

## Testing Checklist

- [ ] Can connect to PostgreSQL: `psql -U rgpv_user -d rgpv_db`
- [ ] Tables exist: `\dt` in psql
- [ ] Flask app starts without errors
- [ ] Can access http://localhost:5000
- [ ] Check enrollment works
- [ ] Save marksheet works
- [ ] Data persists after page reload
- [ ] Logs writing to file

---

## Troubleshooting

### "could not connect to server"
```bash
# Start PostgreSQL
# Windows: net start postgresql-x64-15
# macOS: brew services start postgresql@15
# Linux: sudo systemctl start postgresql
# Docker: docker start rgpv_postgres

# Or check if port 5432 is in use
# Verify DATABASE_URL in .env
```

### "password authentication failed"
```bash
# Reset password
psql -U postgres
ALTER USER rgpv_user WITH PASSWORD 'new_password';
\q

# Update .env with new password
```

### "ModuleNotFoundError: No module named 'psycopg2'"
```bash
# Install dependencies
pip install -r requirements.txt

# Or specifically
pip install psycopg2-binary SQLAlchemy Flask-SQLAlchemy
```

### "relation does not exist"
```bash
# Reinitialize database
python -c "from app_sqlalchemy import app, db; db.create_all()"

# Or using CLI
flask db-init
```

---

## Switching Between Apps

### Use SQLite (OLD)
```bash
# Keep using original:
# python app.py
# Uses SQLite (app.db)
```

### Use PostgreSQL (NEW)
```bash
# Use new app:
# python app_sqlalchemy.py
# Uses PostgreSQL (configured in .env)
```

### Keep Both for Now
```bash
# Both apps can run side-by-side
# SQLite: python app.py (port 5000)
# PostgreSQL: python app_sqlalchemy.py (port 5001)
# Just update PORT in .env
```

---

## Production Deployment

### For Render.com (Easiest)
```bash
# 1. Update requirements.txt - ✅ DONE
# 2. Add app_sqlalchemy.py - ✅ DONE
# 3. Add models.py - ✅ DONE
# 4. Commit to GitHub
git add .
git commit -m "Add PostgreSQL support"
git push origin main

# 5. Render does everything:
# - Creates PostgreSQL instance
# - Sets DATABASE_URL automatically
# - Deploys app_sqlalchemy.py
# - Initializes database
# Done! ✅
```

### Change Render Start Command
```bash
# In Render dashboard:
# Build Command: pip install -r requirements.txt
# Start Command: gunicorn -c gunicorn_config.py app_sqlalchemy:app
```

### Environment Variables in Render
```
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_URL=(auto-provided by Render)
SECRET_KEY=(your random key)
ALLOWED_HOSTS=your-domain.onrender.com
```

---

## Verification Checklist

### Local Development
- [ ] PostgreSQL running (psql command works)
- [ ] Database created (`createdb rgpv_db`)
- [ ] User created (can login with rgpv_user)
- [ ] .env file configured correctly
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Tables created (`flask db-init`)
- [ ] Flask app starts (`python app_sqlalchemy.py`)
- [ ] Can access website (http://localhost:5000)
- [ ] Database operations work (check/save/retrieve)

### Production (Render)
- [ ] Code pushed to GitHub
- [ ] Render PostgreSQL addon created
- [ ] DATABASE_URL shown in environment variables
- [ ] App deployed successfully (no build errors)
- [ ] Health check passes (`curl /health`)
- [ ] Website accessible at your domain
- [ ] Database operations working
- [ ] Logs show no errors

---

## Quick Reference

| Task | Command |
|------|---------|
| Start PostgreSQL | `brew services start postgresql@15` (Mac) or service start (Windows) |
| Create database | `createdb rgpv_db` |
| Connect to database | `psql -U rgpv_user -d rgpv_db` |
| List databases | `\l` (in psql) |
| List tables | `\dt` (in psql) |
| Exit psql | `\q` |
| Install deps | `pip install -r requirements.txt` |
| Initialize DB | `python -c "from app_sqlalchemy import app, db; db.create_all()"` |
| Run app | `python app_sqlalchemy.py` |
| Backup database | `pg_dump -U user -d db > backup.sql` |
| Test connection | `psql -U user -h localhost -d db` |

---

## Next Steps

1. ✅ Choose your installation method (local/Docker/production)
2. ✅ Follow the steps for your path above
3. ✅ Test that everything works
4. ✅ Run migration if you have existing data
5. ✅ Deploy to production
6. ✅ Monitor logs for any issues

---

## Support

- **PostgreSQL Installation**: https://www.postgresql.org/download/
- **Docker Setup**: https://hub.docker.com/_/postgres
- **Render.com Docs**: https://render.com/docs
- **Troubleshooting**: See POSTGRESQL_SETUP_GUIDE.md

---

**Status: ✅ PostgreSQL ready to go!**

**Choose your path and follow the steps above!**
