"""
RGPV Student Result Management System - Production Flask Application
Uses PostgreSQL with SQLAlchemy ORM

Features:
- PostgreSQL database with SQLAlchemy ORM
- Comprehensive error handling
- Request logging
- Security hardening
- Health checks for load balancers
- CORS with whitelist
- Audit logging
"""

import os
import logging
import json
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path
import traceback

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv

from models import db, StudentMarksheet, StudentProfile, AuditLog, init_db

# Load environment variables
load_dotenv()

# ==================== CONFIGURATION ====================
FLASK_ENV = os.getenv('FLASK_ENV', 'production')
DEBUG_MODE = os.getenv('FLASK_DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
DATABASE_URL = os.getenv('DATABASE_URL')
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))  # 16MB

# ==================== LOGGING SETUP ====================
# Create logs directory if it doesn't exist
Path('logs').mkdir(exist_ok=True)

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, LOG_LEVEL))

# File handler with rotation
file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=int(os.getenv('LOG_MAX_SIZE', 10485760)),
    backupCount=int(os.getenv('LOG_BACKUP_COUNT', 10))
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
logger.addHandler(console_handler)


# ==================== FLASK APP INITIALIZATION ====================
def create_app(config=None):
    """Application factory"""
    app = Flask(__name__, template_folder='templates', static_folder='static')
    
    # Configuration
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = DEBUG_MODE
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    
    # CORS Configuration
    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    CORS(app, resources={
        r"/api/*": {"origins": cors_origins, "methods": ["GET", "POST", "PUT", "DELETE"]},
        r"/check": {"origins": cors_origins},
        r"/save": {"origins": cors_origins},
        r"/marksheet/*": {"origins": cors_origins},
    })
    
    # Initialize database
    db.init_app(app)
    with app.app_context():
        db.create_all()
        logger.info("Database initialized successfully")
    
    # Register routes
    register_routes(app)
    register_error_handlers(app)
    
    return app


# Create application instance
app = create_app()


# ==================== ROUTES ====================
def register_routes(app):
    """Register all application routes"""
    
    @app.before_request
    def before_request():
        """Log incoming requests"""
        logger.info(f"{request.method} {request.path} from {request.remote_addr}")
    
    @app.after_request
    def after_request(response):
        """Log outgoing responses"""
        logger.info(f"Response: {response.status_code}")
        return response
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check for load balancers"""
        try:
            # Test database connection
            db.session.execute('SELECT 1')
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'database': 'connected'
            }), 200
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                'status': 'unhealthy',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }), 500
    
    # Check if student exists
    @app.route('/check', methods=['GET'])
    def check_enrollment():
        """Check if enrollment number exists in database"""
        try:
            enrollment = request.args.get('enrollment', '').strip().upper()
            
            # Validate input
            if not enrollment or len(enrollment) < 3:
                return jsonify({
                    'success': False,
                    'error': 'Invalid enrollment number',
                    'status': 400
                }), 400
            
            # Check if student exists
            student = StudentMarksheet.find_by_enrollment(enrollment)
            
            if student:
                logger.info(f"Student found: {enrollment}")
                AuditLog.log_action('check', enrollment, request.remote_addr, 'Student record found')
                return jsonify({
                    'success': True,
                    'found': True,
                    'enrollment': enrollment,
                    'name': student.name,
                    'status': 200
                }), 200
            else:
                logger.info(f"Student not found: {enrollment}")
                AuditLog.log_action('check', enrollment, request.remote_addr, 'Student record not found')
                return jsonify({
                    'success': True,
                    'found': False,
                    'enrollment': enrollment,
                    'status': 404
                }), 404
        
        except Exception as e:
            logger.error(f"Error checking enrollment: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': 'Database error',
                'status': 500
            }), 500
    
    # Save student marksheet
    @app.route('/save', methods=['POST'])
    def save_marksheet():
        """Save or update student marksheet"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided',
                    'status': 400
                }), 400
            
            enrollment = data.get('enrollment', '').strip().upper()
            name = data.get('name', '').strip()
            marksheet_data = data.get('data', {})
            
            # Validate input
            if not enrollment or len(enrollment) < 3:
                return jsonify({
                    'success': False,
                    'error': 'Invalid enrollment number',
                    'status': 400
                }), 400
            
            if not name:
                return jsonify({
                    'success': False,
                    'error': 'Student name required',
                    'status': 400
                }), 400
            
            # Check if student exists
            student = StudentMarksheet.find_by_enrollment(enrollment)
            
            if student:
                # Update existing record
                student.update(marksheet_data)
                logger.info(f"Marksheet updated: {enrollment}")
                AuditLog.log_action('update', enrollment, request.remote_addr, 'Marksheet updated')
                action = 'updated'
            else:
                # Create new record
                student = StudentMarksheet.create(enrollment, name, marksheet_data)
                logger.info(f"New marksheet created: {enrollment}")
                AuditLog.log_action('create', enrollment, request.remote_addr, 'New marksheet created')
                action = 'created'
            
            return jsonify({
                'success': True,
                'message': f'Marksheet {action} successfully',
                'enrollment': enrollment,
                'data': student.to_dict(),
                'status': 200
            }), 200
        
        except Exception as e:
            logger.error(f"Error saving marksheet: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': 'Failed to save marksheet',
                'status': 500
            }), 500
    
    # Get student marksheet
    @app.route('/marksheet/<enrollment>', methods=['GET'])
    def get_marksheet(enrollment):
        """Get student marksheet by enrollment"""
        try:
            enrollment = enrollment.strip().upper()
            
            student = StudentMarksheet.find_by_enrollment(enrollment)
            
            if not student:
                logger.warning(f"Marksheet not found: {enrollment}")
                AuditLog.log_action('view', enrollment, request.remote_addr, 'Marksheet not found')
                return jsonify({
                    'success': False,
                    'error': 'Marksheet not found',
                    'status': 404
                }), 404
            
            logger.info(f"Marksheet retrieved: {enrollment}")
            AuditLog.log_action('view', enrollment, request.remote_addr, 'Marksheet viewed')
            return jsonify({
                'success': True,
                'data': student.to_dict(),
                'status': 200
            }), 200
        
        except Exception as e:
            logger.error(f"Error retrieving marksheet: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': 'Database error',
                'status': 500
            }), 500
    
    # Get student profile
    @app.route('/api/student/<enrollment>', methods=['GET'])
    def get_student_profile(enrollment):
        """Get student profile"""
        try:
            enrollment = enrollment.strip().upper()
            
            # Get marksheet
            marksheet = StudentMarksheet.find_by_enrollment(enrollment)
            if not marksheet:
                return jsonify({
                    'success': False,
                    'error': 'Student not found',
                    'status': 404
                }), 404
            
            # Get profile if exists
            profile = StudentProfile.query.filter_by(enrollment=enrollment).first()
            
            return jsonify({
                'success': True,
                'marksheet': marksheet.to_dict(),
                'profile': profile.to_dict() if profile else None,
                'status': 200
            }), 200
        
        except Exception as e:
            logger.error(f"Error getting student: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Database error',
                'status': 500
            }), 500
    
    # Serve HTML templates
    @app.route('/')
    def index():
        """Serve main page"""
        return render_template('StudentInfoPage.html')
    
    @app.route('/result')
    def result():
        """Serve result page"""
        return render_template('result.html')
    
    @app.route('/marksheet')
    def marksheet():
        """Serve marksheet page"""
        return render_template('marksheet.html')
    
    @app.route('/<filename>')
    def serve_static(filename):
        """Serve static files"""
        allowed_extensions = {'.html', '.css', '.js', '.json', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf'}
        
        ext = os.path.splitext(filename)[1].lower()
        if ext not in allowed_extensions:
            logger.warning(f"Denied file access: {filename}")
            return jsonify({'error': 'File type not allowed'}), 403
        
        try:
            if filename.endswith('.html'):
                return render_template(filename)
            else:
                return send_file(f'static/{filename}')
        except FileNotFoundError:
            logger.warning(f"File not found: {filename}")
            return jsonify({'error': 'File not found'}), 404


# ==================== ERROR HANDLERS ====================
def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(400)
    def bad_request(error):
        logger.warning(f"400 Bad Request: {str(error)}")
        return jsonify({
            'success': False,
            'error': 'Bad request',
            'status': 400
        }), 400
    
    @app.errorhandler(403)
    def forbidden(error):
        logger.warning(f"403 Forbidden: {str(error)}")
        return jsonify({
            'success': False,
            'error': 'Access forbidden',
            'status': 403
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        logger.warning(f"404 Not Found: {request.path}")
        return jsonify({
            'success': False,
            'error': 'Resource not found',
            'status': 404
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 Internal Error: {str(error)}\n{traceback.format_exc()}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'status': 500
        }), 500


# ==================== DATABASE COMMANDS ====================
@app.cli.command()
def init_database():
    """Initialize database with tables"""
    init_db(app)
    print("✅ Database initialized successfully!")


@app.cli.command()
def seed_data():
    """Seed database with sample data"""
    from models import seed_sample_data
    seed_sample_data(app)
    print("✅ Sample data added successfully!")


@app.cli.command()
def reset_database():
    """Reset database (DROP ALL - USE WITH CAUTION!)"""
    confirm = input("⚠️  This will DELETE all data! Type 'yes' to confirm: ")
    if confirm.lower() == 'yes':
        from models import drop_all_tables
        drop_all_tables(app)
        init_db(app)
        print("✅ Database reset successfully!")
    else:
        print("❌ Database reset cancelled")


# ==================== WSGI ENTRY POINT ====================
if __name__ == '__main__':
    # Development only - use Gunicorn/Waitress in production
    logger.info(f"Starting Flask app in {FLASK_ENV} mode")
    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG_MODE,
        use_reloader=DEBUG_MODE
    )
