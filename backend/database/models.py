"""
Database Models Module
SQLAlchemy models for storing performance test data
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import json

Base = declarative_base()

class TestRun(Base):
    """Model for storing test run information"""
    __tablename__ = 'test_runs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_name = Column(String(255), nullable=False)
    environment = Column(String(100), nullable=True)
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Float, nullable=True)
    max_concurrent_users = Column(Integer, nullable=True)
    total_requests = Column(Integer, nullable=True)
    successful_requests = Column(Integer, nullable=True)
    failed_requests = Column(Integer, nullable=True)
    avg_response_time = Column(Float, nullable=True)
    p50_response_time = Column(Float, nullable=True)
    p90_response_time = Column(Float, nullable=True)
    p95_response_time = Column(Float, nullable=True)
    p99_response_time = Column(Float, nullable=True)
    max_response_time = Column(Float, nullable=True)
    min_response_time = Column(Float, nullable=True)
    error_rate = Column(Float, nullable=True)
    throughput = Column(Float, nullable=True)
    status = Column(String(50), nullable=False, default='running')  # running, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    performance_metrics = relationship("PerformanceMetric", back_populates="test_run")
    log_entries = relationship("LogEntry", back_populates="test_run")
    anomalies = relationship("Anomaly", back_populates="test_run")
    reports = relationship("Report", back_populates="test_run")

class PerformanceMetric(Base):
    """Model for storing individual performance metrics"""
    __tablename__ = 'performance_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    response_time = Column(Float, nullable=True)
    throughput = Column(Float, nullable=True)
    concurrent_users = Column(Integer, nullable=True)
    cpu_usage = Column(Float, nullable=True)
    memory_usage = Column(Float, nullable=True)
    status_code = Column(Integer, nullable=True)
    endpoint = Column(String(500), nullable=True)
    request_size = Column(Integer, nullable=True)
    response_size = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    test_run = relationship("TestRun", back_populates="performance_metrics")

class LogEntry(Base):
    """Model for storing log entries"""
    __tablename__ = 'log_entries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=True)
    timestamp = Column(DateTime, nullable=False)
    log_level = Column(String(20), nullable=False)  # INFO, WARN, ERROR, DEBUG
    message = Column(Text, nullable=False)
    source = Column(String(100), nullable=True)  # application, database, network, etc.
    request_id = Column(String(100), nullable=True)
    endpoint = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    response_time = Column(Float, nullable=True)
    status_code = Column(Integer, nullable=True)
    error_type = Column(String(100), nullable=True)
    stack_trace = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    test_run = relationship("TestRun", back_populates="log_entries")

class Anomaly(Base):
    """Model for storing detected anomalies"""
    __tablename__ = 'anomalies'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    anomaly_type = Column(String(50), nullable=False)  # response_time, throughput, error_rate
    metric_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=True)
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    description = Column(Text, nullable=True)
    threshold_value = Column(Float, nullable=True)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    test_run = relationship("TestRun", back_populates="anomalies")

class Report(Base):
    """Model for storing generated reports"""
    __tablename__ = 'reports'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=False)
    report_type = Column(String(50), nullable=False)  # executive, detailed, trends
    format = Column(String(20), nullable=False)  # pdf, excel, html
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    generation_time = Column(Float, nullable=True)  # seconds
    status = Column(String(20), nullable=False, default='pending')  # pending, generating, completed, failed
    error_message = Column(Text, nullable=True)
    download_count = Column(Integer, default=0)
    last_downloaded = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    test_run = relationship("TestRun", back_populates="reports")

class Configuration(Base):
    """Model for storing application configuration"""
    __tablename__ = 'configurations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), nullable=False, unique=True)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)  # thresholds, alerts, general
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Alert(Base):
    """Model for storing performance alerts"""
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=True)
    alert_type = Column(String(50), nullable=False)  # threshold_breach, anomaly, error_spike
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    metric_name = Column(String(100), nullable=True)
    metric_value = Column(Float, nullable=True)
    threshold_value = Column(Float, nullable=True)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    notification_sent = Column(Boolean, default=False)
    notification_sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    test_run = relationship("TestRun")

class Trend(Base):
    """Model for storing performance trends"""
    __tablename__ = 'trends'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_name = Column(String(100), nullable=False)
    time_period = Column(String(20), nullable=False)  # hourly, daily, weekly, monthly
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    avg_value = Column(Float, nullable=True)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    std_deviation = Column(Float, nullable=True)
    trend_direction = Column(String(20), nullable=True)  # increasing, decreasing, stable
    trend_strength = Column(Float, nullable=True)  # correlation coefficient
    sample_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Baseline(Base):
    """Model for storing performance baselines"""
    __tablename__ = 'baselines'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    environment = Column(String(100), nullable=True)
    test_type = Column(String(100), nullable=True)
    avg_response_time = Column(Float, nullable=True)
    p95_response_time = Column(Float, nullable=True)
    p99_response_time = Column(Float, nullable=True)
    max_throughput = Column(Float, nullable=True)
    max_error_rate = Column(Float, nullable=True)
    baseline_data = Column(Text, nullable=True)  # JSON string for additional data
    is_active = Column(Boolean, default=True)
    version = Column(String(50), nullable=True)
    created_by = Column(String(100), nullable=True)
    approved_by = Column(String(100), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Utility functions for models
def to_dict(instance):
    """Convert SQLAlchemy instance to dictionary"""
    return {c.key: getattr(instance, c.key) for c in instance.__table__.columns}

def from_dict(model_class, data_dict):
    """Create SQLAlchemy instance from dictionary"""
    return model_class(**{k: v for k, v in data_dict.items() 
                         if k in [c.key for c in model_class.__table__.columns]}) 