"""
Database models for SmartTest Insight Generator
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import json

Base = declarative_base()

class UploadedFile(Base):
    """Model for storing uploaded files and their metadata"""
    
    __tablename__ = 'uploaded_files'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)  # xlsx, csv, json
    upload_date = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    total_records = Column(Integer, default=0)
    metrics_json = Column(Text)  # Store processed metrics as JSON
    summary_json = Column(Text)  # Store data summary as JSON
    is_active = Column(Boolean, default=True)  # For soft deletion
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'processed': self.processed,
            'total_records': self.total_records,
            'metrics': json.loads(self.metrics_json) if self.metrics_json else None,
            'summary': json.loads(self.summary_json) if self.summary_json else None,
            'is_active': self.is_active
        }

class ComparisonReport(Base):
    """Model for storing comparison reports"""
    
    __tablename__ = 'comparison_reports'
    
    id = Column(Integer, primary_key=True)
    file_a_id = Column(Integer, nullable=False)
    file_b_id = Column(Integer, nullable=False)
    report_path = Column(String(500))
    report_size = Column(Integer)
    created_date = Column(DateTime, default=datetime.utcnow)
    report_type = Column(String(50), default='pdf')  # pdf, html, excel
    is_active = Column(Boolean, default=True)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'file_a_id': self.file_a_id,
            'file_b_id': self.file_b_id,
            'report_path': self.report_path,
            'report_size': self.report_size,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'report_type': self.report_type,
            'is_active': self.is_active
        }

# Database setup
def init_database():
    """Initialize the database"""
    from config import Config
    
    # Create database engine
    engine = create_engine(Config.DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return SessionLocal

def get_db():
    """Get database session"""
    SessionLocal = init_database()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 