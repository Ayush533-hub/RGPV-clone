"""
Database models for RGPV Student Result Management System
Using SQLAlchemy ORM with PostgreSQL
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

# Initialize SQLAlchemy
db = SQLAlchemy()


class StudentMarksheet(db.Model):
    """
    Student marksheet model - stores student result data
    
    Attributes:
        id: Primary key (auto-increment)
        enrollment: Student enrollment number (unique)
        name: Student name
        data: JSON data containing all marksheet information
        created_at: Timestamp when record created
        updated_at: Timestamp when record last updated
    """
    __tablename__ = 'student_marksheets'
    
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    enrollment = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    data = db.Column(db.JSON, nullable=True)  # Stores complete marksheet as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<StudentMarksheet {self.enrollment} - {self.name}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'enrollment': self.enrollment,
            'name': self.name,
            'data': self.data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def find_by_enrollment(cls, enrollment):
        """Find student by enrollment number"""
        return cls.query.filter_by(enrollment=enrollment).first()
    
    @classmethod
    def create(cls, enrollment, name, data=None):
        """Create new student marksheet"""
        student = cls(enrollment=enrollment, name=name, data=data)
        db.session.add(student)
        db.session.commit()
        return student
    
    def update(self, data):
        """Update student marksheet data"""
        self.data = data
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self
    
    def delete(self):
        """Delete student marksheet"""
        db.session.delete(self)
        db.session.commit()


class StudentProfile(db.Model):
    """
    Student profile model - stores additional student information
    
    Attributes:
        id: Primary key
        enrollment: Student enrollment number (foreign key)
        email: Student email
        phone: Student phone number
        semester: Current semester
        branch: Student branch/department
        created_at: Profile creation timestamp
    """
    __tablename__ = 'student_profiles'
    
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    enrollment = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(15), nullable=True)
    semester = db.Column(db.Integer, nullable=True)
    branch = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<StudentProfile {self.enrollment}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'enrollment': self.enrollment,
            'email': self.email,
            'phone': self.phone,
            'semester': self.semester,
            'branch': self.branch,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class AuditLog(db.Model):
    """
    Audit log model - tracks all changes for security/compliance
    
    Attributes:
        id: Primary key
        action: Action performed (create, update, delete, download, etc.)
        enrollment: Student enrollment number (if applicable)
        user_info: IP address / user information
        timestamp: When action occurred
        details: Additional details about the action
    """
    __tablename__ = 'audit_logs'
    
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50), nullable=False)  # create, update, delete, view
    enrollment = db.Column(db.String(20), nullable=True, index=True)
    user_info = db.Column(db.String(255), nullable=True)  # IP address
    details = db.Column(db.Text, nullable=True)  # Additional info
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<AuditLog {self.action} - {self.timestamp}>'
    
    @classmethod
    def log_action(cls, action, enrollment=None, user_info=None, details=None):
        """Log an action"""
        log = cls(
            action=action,
            enrollment=enrollment,
            user_info=user_info,
            details=details
        )
        db.session.add(log)
        db.session.commit()
        return log


# Database initialization functions
def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    with app.app_context():
        db.create_all()


def create_tables(app):
    """Create all tables"""
    init_db(app)


def drop_all_tables(app):
    """Drop all tables (USE WITH CAUTION!)"""
    with app.app_context():
        db.drop_all()


def seed_sample_data(app):
    """Seed database with sample data for testing"""
    with app.app_context():
        # Check if data already exists
        if StudentMarksheet.query.first():
            print("Database already has data. Skipping seed.")
            return
        
        # Create sample student
        sample_marksheet = StudentMarksheet(
            enrollment="2021001",
            name="Raj Kumar",
            data={
                "semester": 5,
                "branch": "CSE",
                "subjects": {
                    "DBMS": {"internal": 15, "external": 45, "total": 60},
                    "OS": {"internal": 14, "external": 42, "total": 56},
                    "CN": {"internal": 16, "external": 48, "total": 64},
                },
                "sgpa": 7.8,
                "cgpa": 7.5
            }
        )
        db.session.add(sample_marksheet)
        db.session.commit()
        print("Sample data created successfully!")
