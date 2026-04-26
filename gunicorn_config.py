"""
Gunicorn Configuration File
Save as: gunicorn_config.py

Run with: gunicorn -c gunicorn_config.py app:app
"""

import os
import multiprocessing
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# Server Socket
# ==========================================
# IP address and port to bind to
host = os.getenv("HOST", "0.0.0.0")
port = int(os.getenv("PORT", 8000))
bind = f"{host}:{port}"

# ==========================================
# Worker Configuration
# ==========================================
# Number of worker processes
# Formula: (2 x CPU cores) + 1
workers = int(os.getenv("WORKERS", multiprocessing.cpu_count() * 2 + 1))

# Worker class
# 'sync': Default, one request per worker
# 'gthread': Threaded workers
# 'gevent': Asynchronous, requires gevent
worker_class = "sync"

# Number of worker threads (for gthread worker class)
threads = 4

# Worker timeout (seconds) - time before worker is killed and restarted
timeout = int(os.getenv("TIMEOUT", 30))

# Keep alive timeout
keepalive = 5

# ==========================================
# Logging
# ==========================================
# Access log
accesslog = "logs/access.log"

# Error log
errorlog = "logs/error.log"

# Log level
loglevel = os.getenv("LOG_LEVEL", "info")

# Log format
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# ==========================================
# Process Naming
# ==========================================
# Set worker process names
proc_name = "rgpv-app"

# ==========================================
# Server Mechanics
# ==========================================
# Daemon mode (run in background)
daemon = False

# PID file
pidfile = "logs/gunicorn.pid"

# Limit the allowed size of an HTTP request line
limit_request_line = 4094

# Limit the allowed size of an HTTP request fields
limit_request_fields = 100

# Limit the allowed size of an HTTP request body
limit_request_body = 16777216  # 16MB

# ==========================================
# SSL/TLS (if needed)
# ==========================================
# SSL certificate file
# certfile = "/path/to/cert.pem"

# SSL key file
# keyfile = "/path/to/key.pem"

# ==========================================
# App Settings
# ==========================================
# Whether to forward allow-ips header
forwarded_allow_ips = "*"

# Proxy protocol version to accept
# proxy_protocol = True

# ==========================================
# Hooks (Optional)
# ==========================================

def on_starting(server):
    """Called just before Gunicorn starts"""
    print("[Gunicorn] Starting RGPV Flask Application")

def on_exit(server):
    """Called just before Gunicorn exits"""
    print("[Gunicorn] Shutting down gracefully")

def when_ready(server):
    """Called when server is ready"""
    print(f"[Gunicorn] Server is ready. Spawning {workers} workers")

def worker_int(worker):
    """Called when a worker receives SIGINT"""
    print(f"[Gunicorn] Worker {worker.pid} received SIGINT")

def worker_abort(worker):
    """Called when a worker is aborted"""
    print(f"[Gunicorn] Worker {worker.pid} aborted")
