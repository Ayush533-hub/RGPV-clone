# 🗄️ POSTGRESQL DATABASE SETUP GUIDE

## Table of Contents
1. [Quick Start](#quick-start)
2. [PostgreSQL Installation](#postgresql-installation)
3. [Database Setup](#database-setup)
4. [Local Development Setup](#local-development-setup)
5. [Migration from SQLite to PostgreSQL](#migration-from-sqlite-to-postgresql)
6. [Remote Database Setup](#remote-database-setup)
7. [Docker PostgreSQL](#docker-postgresql)
8. [Common Issues & Troubleshooting](#troubleshooting)
9. [Backup & Restore](#backup--restore)
10. [Security Best Practices](#security-best-practices)

---

## Quick Start

### For Local Development (5 minutes)
```bash
# 1. Install PostgreSQL (see section below)
# 2. Create database
createdb rgpv_db

# 3. Update requirements
pip install -r requirements.txt

# 4. Update .env file
cp .env.postgresql .env
nano .env

# 5. Run migrations
flask db upgrade

# 6. Start app
python app_sqlalchemy.py
```

### For Production (Render.com)
```bash
# Just push to GitHub - Render provides DATABASE_URL automatically!
git add .
git commit -m "Switch to PostgreSQL"
git push origin main
```

---

## PostgreSQL Installation

### Windows
```bash
# Option 1: PostgreSQL Installer
1. Download: https://www.postgresql.org/download/windows/
2. Run installer (choose version 14 or higher)
3. Choose:
   - Installation directory: C:\Program Files\PostgreSQL\14
   - Port: 5432
   - Password: your_secure_password
   - Admin user: postgres
4. Complete installation
5. Open pgAdmin (should launch automatically)

# Option 2: Chocolatey (if installed)
choco install postgresql

# Verify installation
psql --version
```

### macOS
```bash
# Using Homebrew (recommended)
brew install postgresql@15
brew services start postgresql@15

# Verify installation
psql --version

# Create initial database
createdb
```

### Linux (Ubuntu/Debian)
```bash
# Update package list
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Start service
sudo systemctl start postgresql

# Verify installation
sudo -u postgres psql --version
```

### Docker (Easiest for Windows)
```bash
# Install Docker Desktop from: https://www.docker.com/products/docker-desktop

# Create and run PostgreSQL container
docker run --name rgpv_postgres \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=rgpv_db \
  -p 5432:5432 \
  -d postgres:15

# Verify it's running
docker ps
```

---

## Database Setup

### Create Database Locally

#### Windows/macOS (psql)
```bash
# Connect as default user
psql -U postgres

# In psql prompt, run:
CREATE DATABASE rgpv_db;
CREATE USER rgpv_user WITH PASSWORD 'your_secure_password';
ALTER ROLE rgpv_user SET client_encoding TO 'utf8';
ALTER ROLE rgpv_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE rgpv_user SET default_transaction_deferrable TO on;
ALTER ROLE rgpv_user SET default_transaction_isolation TO 'read committed';
GRANT ALL PRIVILEGES ON DATABASE rgpv_db TO rgpv_user;

# Exit psql
\q
```

#### Linux (as sudo)
```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE rgpv_db;
CREATE USER rgpv_user WITH PASSWORD 'your_secure_password';
ALTER ROLE rgpv_user SET client_encoding TO 'utf8';
GRANT ALL PRIVILEGES ON DATABASE rgpv_db TO rgpv_user;

# Exit
\q
```

### Verify Connection
```bash
# Test connection
psql -U rgpv_user -h localhost -d rgpv_db

# In psql, run:
\dt  # List tables (should be empty)
\q   # Exit
```

---

## Local Development Setup

### Step 1: Install Dependencies
```bash
# Create virtual environment (if not done)
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
# Copy PostgreSQL env file
cp .env.postgresql .env

# Edit .env
nano .env

# Update these values:
# DATABASE_URL=postgresql://rgpv_user:your_password@localhost:5432/rgpv_db
# FLASK_DEBUG=True (for development only!)
# SECRET_KEY=your_dev_secret_key
```

### Step 3: Initialize Database
```bash
# Using Flask CLI
flask db-init

# Or using Python
python -c "from app_sqlalchemy import app, db; db.create_all()"

# Verify tables created
psql -U rgpv_user -d rgpv_db -c "\dt"
```

### Step 4: Seed Sample Data
```bash
# Using Flask CLI
flask seed-data

# Or using Python
python -c "from models import seed_sample_data; from app_sqlalchemy import app; seed_sample_data(app)"
```

### Step 5: Run Application
```bash
# Development mode
python app_sqlalchemy.py

# Or with Gunicorn (test production)
gunicorn -c gunicorn_config.py app_sqlalchemy:app
```

---

## Migration from SQLite to PostgreSQL

### Step 1: Export Data from SQLite
```python
# Create migration script: migrate_to_postgres.py
import sqlite3
import json
from models import db, StudentMarksheet
from app_sqlalchemy import app

# Read from SQLite
sqlite_conn = sqlite3.connect('app.db')
sqlite_conn.row_factory = sqlite3.Row
cursor = sqlite_conn.cursor()

cursor.execute("SELECT * FROM marksheets")
rows = cursor.fetchall()

# Print data to verify
print(f"Found {len(rows)} records in SQLite")
for row in rows:
    print(dict(row))

sqlite_conn.close()
```

### Step 2: Import Data to PostgreSQL
```python
# Create import script: import_to_postgres.py
import sqlite3
import json
from models import db, StudentMarksheet
from app_sqlalchemy import app

with app.app_context():
    # Connect to SQLite
    sqlite_conn = sqlite3.connect('app.db')
    sqlite_conn.row_factory = sqlite3.Row
    cursor = sqlite_conn.cursor()
    
    # Read all records
    cursor.execute("SELECT * FROM marksheets")
    rows = cursor.fetchall()
    
    # Import to PostgreSQL
    for row in rows:
        try:
            student = StudentMarksheet(
                enrollment=row['enrollment'],
                name=row.get('name', 'Unknown'),
                data=json.loads(row['data']) if isinstance(row['data'], str) else row['data']
            )
            db.session.add(student)
            print(f"✅ Imported: {row['enrollment']}")
        except Exception as e:
            print(f"❌ Failed {row['enrollment']}: {e}")
    
    # Commit all
    db.session.commit()
    print("\n✅ Migration complete!")
    
    sqlite_conn.close()
```

### Step 3: Run Migration
```bash
# Make sure .env points to PostgreSQL
python import_to_postgres.py

# Verify data in PostgreSQL
psql -U rgpv_user -d rgpv_db -c "SELECT COUNT(*) FROM student_marksheets;"
```

---

## Remote Database Setup

### Option 1: Render.com (Recommended - Auto Provision)
```bash
# Push code to GitHub
git add .
git commit -m "Add PostgreSQL support"
git push origin main

# Render will automatically:
# 1. Create PostgreSQL instance
# 2. Set DATABASE_URL environment variable
# 3. Connect your app
# No manual setup needed! ✨
```

### Option 2: Amazon RDS
```bash
# 1. Create RDS instance in AWS Console
# 2. Get connection string
# 3. Add to .env (also in Render dashboard):
DATABASE_URL=postgresql://user:password@instance.rds.amazonaws.com:5432/rgpv_db

# 4. Test connection
psql -U username -h instance.rds.amazonaws.com -d rgpv_db
```

### Option 3: Railway.app
```bash
# 1. Push to GitHub
# 2. Create new project in Railway
# 3. Add PostgreSQL plugin
# 4. Railway auto-generates DATABASE_URL
# 5. Deploy! 🚀
```

### Option 4: Heroku PostgreSQL (Legacy but still works)
```bash
# Install Heroku CLI
npm install -g heroku

# Login
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git push heroku main

# View DATABASE_URL
heroku config:get DATABASE_URL
```

---

## Docker PostgreSQL

### Using docker-compose
```yaml
# docker-compose.yml updated for PostgreSQL
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: rgpv_db
      POSTGRES_USER: rgpv_user
      POSTGRES_PASSWORD: your_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U rgpv_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    build: .
    command: gunicorn -c gunicorn_config.py app_sqlalchemy:app
    ports:
      - "8000:5000"
    environment:
      DATABASE_URL: postgresql://rgpv_user:your_password@db:5432/rgpv_db
      FLASK_ENV: production
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs

volumes:
  postgres_data:
```

### Run with Docker
```bash
# Build and start
docker-compose up -d

# Verify services
docker-compose ps

# View logs
docker-compose logs -f web

# Stop
docker-compose down

# Stop and remove volumes (WARNING: deletes data!)
docker-compose down -v
```

---

## Troubleshooting

### Connection Refused
```bash
# Problem: psycopg2.OperationalError: could not connect to server
# Did you start PostgreSQL?

# Windows
# Check if PostgreSQL service is running:
net start | findstr PostgreSQL

# Start service
net start postgresql-x64-15

# macOS
# Restart Homebrew PostgreSQL:
brew services restart postgresql@15

# Linux
sudo systemctl restart postgresql

# Docker
docker ps  # Check if container is running
docker start rgpv_postgres
```

### Wrong Password
```bash
# Problem: FATAL: password authentication failed

# Reset password (Windows/macOS)
psql -U postgres

# In psql:
ALTER USER rgpv_user WITH PASSWORD 'new_password';
\q

# Update .env:
DATABASE_URL=postgresql://rgpv_user:new_password@localhost:5432/rgpv_db
```

### Database Doesn't Exist
```bash
# Problem: FATAL: database "rgpv_db" does not exist

# Create it:
createdb rgpv_db

# Or in psql:
psql -U postgres
CREATE DATABASE rgpv_db;
\q
```

### Port Already in Use
```bash
# Problem: could not bind to 0.0.0.0:5432

# Find what's using port 5432
# Windows:
netstat -ano | findstr :5432

# macOS/Linux:
lsof -i :5432

# Use different port in .env:
DATABASE_URL=postgresql://user:pass@localhost:5433/rgpv_db
```

### Import Errors
```bash
# Problem: ModuleNotFoundError: No module named 'psycopg2'

# Install missing packages:
pip install -r requirements.txt

# Verify installation:
python -c "import psycopg2; print(psycopg2.__version__)"
```

---

## Backup & Restore

### Backup Database
```bash
# Backup to file
pg_dump -U rgpv_user -d rgpv_db -h localhost > backup.sql

# Compressed backup (recommended)
pg_dump -U rgpv_user -d rgpv_db -h localhost | gzip > backup.sql.gz

# For AWS RDS
pg_dump -U rgpv_user -h instance.rds.amazonaws.com -d rgpv_db > backup.sql
```

### Restore Database
```bash
# From backup file
psql -U rgpv_user -d rgpv_db -h localhost < backup.sql

# From compressed backup
gunzip -c backup.sql.gz | psql -U rgpv_user -d rgpv_db -h localhost

# Create fresh database and restore
dropdb -U rgpv_user -h localhost rgpv_db
createdb -U rgpv_user -h localhost rgpv_db
psql -U rgpv_user -d rgpv_db -h localhost < backup.sql
```

### Automated Backup Script
```bash
#!/bin/bash
# backup_postgres.sh

BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DATABASE="rgpv_db"
USER="rgpv_user"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup with timestamp
pg_dump -U $USER -d $DATABASE -h localhost | gzip > "$BACKUP_DIR/backup_$DATE.sql.gz"

# Keep only last 7 days of backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "✅ Backup created: $BACKUP_DIR/backup_$DATE.sql.gz"
```

### Schedule Automated Backups
```bash
# Linux - Add to crontab
crontab -e

# Add line for daily backup at 2 AM
0 2 * * * /path/to/backup_postgres.sh

# macOS - Use LaunchAgent (similar approach)
```

---

## Security Best Practices

### 1. Strong Passwords
```sql
-- Generate strong password
-- Use: python -c "import secrets; print(secrets.token_urlsafe(32))"

-- Set strong password
ALTER USER rgpv_user WITH PASSWORD 'your_very_strong_random_password_here';
```

### 2. User Permissions
```sql
-- Create limited user (production)
CREATE USER rgpv_readonly WITH PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE rgpv_db TO rgpv_readonly;
GRANT USAGE ON SCHEMA public TO rgpv_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO rgpv_readonly;

-- Create admin user
CREATE USER rgpv_admin WITH PASSWORD 'admin_password';
GRANT ALL PRIVILEGES ON DATABASE rgpv_db TO rgpv_admin;
```

### 3. SSL/TLS Connection
```bash
# In .env (for remote databases)
DATABASE_URL=postgresql://user:pass@host:5432/rgpv_db?sslmode=require

# For AWS RDS (always use SSL)
DATABASE_URL=postgresql://user:pass@instance.rds.amazonaws.com:5432/rgpv_db?sslmode=require
```

### 4. Firewall Rules
```bash
# Only allow app server to connect
# AWS RDS Security Group:
# - Source: Your app server IP
# - Protocol: PostgreSQL (5432)
# - Port: 5432

# Digital Ocean:
# - Add firewall rule
# - Inbound: PostgreSQL (5432) from app server
```

### 5. Audit Logging
```sql
-- Enable query logging
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_duration = 'on';
SELECT pg_reload_conf();

-- Check logs
SELECT * FROM pg_stat_statements;
```

### 6. .env Security
```bash
# Never commit .env file!
# .gitignore should have:
.env
.env.local
.env.*.local

# Keep .env.example safe with no secrets:
DATABASE_URL=postgresql://user:password@localhost:5432/rgpv_db
SECRET_KEY=your_secret_key_here
```

---

## Summary

| Task | Command |
|------|---------|
| Install PostgreSQL | See installation section above |
| Create database | `createdb rgpv_db` |
| Create user | `psql -U postgres` then SQL commands |
| Update .env | `cp .env.postgresql .env && nano .env` |
| Install packages | `pip install -r requirements.txt` |
| Initialize tables | `flask db-init` |
| Add sample data | `flask seed-data` |
| Run app (dev) | `python app_sqlalchemy.py` |
| Backup database | `pg_dump -U user -d db > backup.sql` |
| Deploy to Render | `git push origin main` |

---

## Next Steps

1. ✅ Install PostgreSQL
2. ✅ Create database and user
3. ✅ Update .env with database URL
4. ✅ Install Python packages: `pip install -r requirements.txt`
5. ✅ Initialize database: `flask db-init`
6. ✅ Test app locally: `python app_sqlalchemy.py`
7. ✅ Deploy to Render/production

---

## Resources

- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **psycopg2 Docs**: https://www.psycopg.org/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Flask-SQLAlchemy**: https://flask-sqlalchemy.palletsprojects.com/
- **Render.com Docs**: https://render.com/docs
- **PostgreSQL Tutorial**: https://www.postgresql.org/docs/current/tutorial.html

**Status: ✅ Ready to use PostgreSQL!**
