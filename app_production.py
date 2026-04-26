"""
RGPV Student Result Management System - Production Ready
Production-grade Flask application with proper error handling, logging, and security.
"""

from flask import Flask, request, jsonify, Response, send_file, render_template_string
from flask_cors import CORS
import sqlite3
import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# ============ CONFIGURATION ============

app = Flask(__name__)

# Security Configuration
app.config['JSON_SORT_KEYS'] = False
SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-in-production")
if os.getenv("FLASK_ENV") == "production" and SECRET_KEY == "dev-key-change-in-production":
    raise ValueError("ERROR: SECRET_KEY not set in production! Set it in .env")

# Database Configuration
DB_DIR = os.getenv("DB_BACKUP_PATH", "data")
os.makedirs(DB_DIR, exist_ok=True)
DB_NAME = os.path.join(DB_DIR, "data.db")

# Logging Directory
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# CORS Configuration - IMPORTANT: Don't allow all origins in production
ALLOWED_ORIGINS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
cors_config = {
    "resources": {
        r"/*": {
            "origins": ALLOWED_ORIGINS,
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "max_age": 3600
        }
    }
}
CORS(app, resources=cors_config)

# ============ LOGGING SETUP ============

def setup_logging():
    """Configure logging with rotation"""
    if not app.debug:
        # File handler with rotation
        file_handler = RotatingFileHandler(
            os.path.join(LOG_DIR, 'app.log'),
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        app.logger.addHandler(console_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info("Logging initialized")

setup_logging()

# ============ DATABASE FUNCTIONS ============

def get_db_connection():
    """Get database connection with proper error handling"""
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        app.logger.error(f"Database connection error: {e}")
        raise

def init_db():
    """Initialize database with proper error handling"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS marksheets (
                        enrollment TEXT PRIMARY KEY,
                        data TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )''')
        conn.commit()
        conn.close()
        app.logger.info("Database initialized successfully")
    except sqlite3.Error as e:
        app.logger.error(f"Database initialization error: {e}")
        raise

# Initialize database on startup
try:
    init_db()
except Exception as e:
    app.logger.critical(f"Failed to initialize database: {e}")

# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    app.logger.warning(f"404 error: {request.path}")
    return jsonify({
        "success": False,
        "error": "Resource not found",
        "status": 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    app.logger.error(f"500 error: {error}")
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "status": 500
    }), 500

@app.errorhandler(403)
def forbidden(error):
    """Handle 403 errors"""
    app.logger.warning(f"403 error: Forbidden access from {request.remote_addr}")
    return jsonify({
        "success": False,
        "error": "Forbidden",
        "status": 403
    }), 403

@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors"""
    app.logger.warning(f"400 error: Bad request")
    return jsonify({
        "success": False,
        "error": "Bad request",
        "status": 400
    }), 400

# ============ ROUTES: HTML SERVING ============

@app.route('/')
def index():
    """Serve index page"""
    try:
        app.logger.info(f"Index page requested from {request.remote_addr}")
        return send_file('StudentInfoPage.html')
    except FileNotFoundError:
        app.logger.error("StudentInfoPage.html not found")
        return jsonify({"error": "Page not found"}), 404
    except Exception as e:
        app.logger.error(f"Error serving index: {e}")
        return jsonify({"error": "Error loading page"}), 500

@app.route('/health')
def health():
    """Health check endpoint for load balancers"""
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()}), 200
    except Exception as e:
        app.logger.error(f"Health check failed: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route('/<filename>')
def serve_static(filename):
    """Serve static files (HTML, CSS, JS, Images)"""
    try:
        # Whitelist allowed file extensions
        allowed_extensions = {'.html', '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.mp4'}
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            app.logger.warning(f"Attempted to access disallowed file: {filename}")
            return jsonify({"error": "File type not allowed"}), 403
        
        if os.path.exists(filename) and os.path.isfile(filename):
            app.logger.info(f"Serving static file: {filename}")
            return send_file(filename)
        else:
            app.logger.warning(f"Static file not found: {filename}")
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        app.logger.error(f"Error serving static file {filename}: {e}")
        return jsonify({"error": "Error loading file"}), 500

# ============ ROUTES: API ENDPOINTS ============

@app.route("/check", methods=["GET"])
def check_enrollment():
    """
    Check if enrollment exists in database
    Query params: enrollment (required)
    """
    try:
        enrollment = request.args.get("enrollment", "").strip()
        
        # Validate input
        if not enrollment:
            app.logger.warning(f"Check request without enrollment number from {request.remote_addr}")
            return jsonify({
                "success": False,
                "error": "Enrollment number is required"
            }), 400
        
        app.logger.info(f"Checking enrollment: {enrollment}")
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT data FROM marksheets WHERE enrollment=?", (enrollment,))
        row = c.fetchone()
        conn.close()
        
        if row:
            app.logger.info(f"Enrollment found: {enrollment}")
            return jsonify({
                "success": True,
                "exists": True,
                "data": row[0]
            }), 200
        else:
            app.logger.info(f"Enrollment not found: {enrollment}")
            return jsonify({
                "success": True,
                "exists": False
            }), 200
            
    except sqlite3.Error as e:
        app.logger.error(f"Database error in check_enrollment: {e}")
        return jsonify({
            "success": False,
            "error": "Database error"
        }), 500
    except Exception as e:
        app.logger.error(f"Unexpected error in check_enrollment: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500

@app.route("/save", methods=["POST"])
def save_marksheet():
    """
    Save or update student marksheet
    Body: {"enrollment": "...", "data": "..."}
    """
    try:
        # Parse JSON
        data = request.get_json()
        if not data:
            app.logger.warning(f"Save request with no JSON from {request.remote_addr}")
            return jsonify({
                "success": False,
                "error": "Request body must be JSON"
            }), 400
        
        enrollment = data.get("enrollment", "").strip()
        content = data.get("data", "").strip()
        
        # Validate input
        if not enrollment or not content:
            app.logger.warning(f"Save request with missing data from {request.remote_addr}")
            return jsonify({
                "success": False,
                "error": "Missing enrollment or data"
            }), 400
        
        # Prevent injection attacks - validate enrollment format
        if not enrollment.isalnum():
            app.logger.warning(f"Invalid enrollment format: {enrollment}")
            return jsonify({
                "success": False,
                "error": "Invalid enrollment format"
            }), 400
        
        app.logger.info(f"Saving marksheet for enrollment: {enrollment}")
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""
            REPLACE INTO marksheets (enrollment, data, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (enrollment, content))
        conn.commit()
        conn.close()
        
        app.logger.info(f"Marksheet saved successfully for enrollment: {enrollment}")
        return jsonify({
            "success": True,
            "message": "Marksheet saved successfully",
            "enrollment": enrollment
        }), 200
        
    except sqlite3.Error as e:
        app.logger.error(f"Database error in save_marksheet: {e}")
        return jsonify({
            "success": False,
            "error": "Database error while saving"
        }), 500
    except Exception as e:
        app.logger.error(f"Unexpected error in save_marksheet: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500

@app.route("/marksheet/<enrollment>", methods=["GET"])
def show_marksheet(enrollment):
    """
    Retrieve and display saved marksheet
    """
    try:
        enrollment = enrollment.strip()
        
        if not enrollment:
            app.logger.warning(f"Show marksheet request without enrollment")
            return jsonify({"error": "Enrollment number required"}), 400
        
        app.logger.info(f"Retrieving marksheet for enrollment: {enrollment}")
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT data FROM marksheets WHERE enrollment=?", (enrollment,))
        row = c.fetchone()
        conn.close()
        
        if row:
            app.logger.info(f"Marksheet retrieved for enrollment: {enrollment}")
            return Response(row[0], mimetype="text/html")
        else:
            app.logger.warning(f"Marksheet not found for enrollment: {enrollment}")
            return "<h2>No record found for enrollment: {}</h2>".format(enrollment), 404
            
    except sqlite3.Error as e:
        app.logger.error(f"Database error in show_marksheet: {e}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error in show_marksheet: {e}")
        return jsonify({"error": "Internal server error"}), 500

# ============ PRODUCTION VS DEVELOPMENT ============

def create_app():
    """Application factory function"""
    return app

if __name__ == "__main__":
    # Load configuration from environment
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 5000))
    
    # Warning for production
    if not DEBUG:
        app.logger.warning("=" * 50)
        app.logger.warning("PRODUCTION MODE ENABLED")
        app.logger.warning("Debug mode is OFF")
        app.logger.warning("Using Flask development server")
        app.logger.warning("For production, use Gunicorn or Waitress")
        app.logger.warning("=" * 50)
    
    # Run application
    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG,
        use_reloader=DEBUG,
        use_debugger=DEBUG
    )
