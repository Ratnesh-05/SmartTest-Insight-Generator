"""
Database Connection Module
Handles database connections, sessions, and operations using SQLAlchemy
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator, Optional, Dict, Any, List
import logging
import os
from .models import Base, TestRun, PerformanceMetric, LogEntry, Anomaly, Report

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database manager
        
        Args:
            database_url: Database connection URL (defaults to SQLite)
        """
        if database_url is None:
            # Default to SQLite for simplicity
            database_url = "sqlite:///smarttest_insights.db"
        
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
        self._setup_database()
    
    def _setup_database(self):
        """Setup database engine and session factory"""
        try:
            # Create engine with appropriate settings
            if self.database_url.startswith('sqlite'):
                self.engine = create_engine(
                    self.database_url,
                    connect_args={"check_same_thread": False},
                    poolclass=StaticPool,
                    echo=False  # Set to True for SQL debugging
                )
            else:
                self.engine = create_engine(
                    self.database_url,
                    pool_pre_ping=True,
                    pool_recycle=3600,
                    echo=False
                )
            
            # Create session factory
            self.SessionLocal = scoped_session(
                sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            )
            
            logger.info(f"Database engine created successfully: {self.database_url}")
            
        except Exception as e:
            logger.error(f"Error setting up database: {str(e)}")
            raise
    
    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            raise
    
    def drop_tables(self):
        """Drop all database tables"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Error dropping tables: {str(e)}")
            raise
    
    @contextmanager
    def get_session(self) -> Generator:
        """
        Get database session with automatic cleanup
        
        Returns:
            Database session
        """
        session = self.SessionLocal()
        try:
            yield session
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_session_sync(self):
        """Get synchronous database session"""
        return self.SessionLocal()
    
    def close_connections(self):
        """Close all database connections"""
        try:
            self.SessionLocal.remove()
            if self.engine:
                self.engine.dispose()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {str(e)}")

class TestRunRepository:
    """Repository for TestRun operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_test_run(self, test_data: Dict[str, Any]) -> TestRun:
        """Create a new test run"""
        with self.db_manager.get_session() as session:
            test_run = TestRun(**test_data)
            session.add(test_run)
            session.commit()
            session.refresh(test_run)
            return test_run
    
    def get_test_run(self, test_run_id: int) -> Optional[TestRun]:
        """Get test run by ID"""
        with self.db_manager.get_session() as session:
            return session.query(TestRun).filter(TestRun.id == test_run_id).first()
    
    def update_test_run(self, test_run_id: int, update_data: Dict[str, Any]) -> Optional[TestRun]:
        """Update test run"""
        with self.db_manager.get_session() as session:
            test_run = session.query(TestRun).filter(TestRun.id == test_run_id).first()
            if test_run:
                for key, value in update_data.items():
                    if hasattr(test_run, key):
                        setattr(test_run, key, value)
                session.commit()
                session.refresh(test_run)
            return test_run
    
    def get_recent_test_runs(self, limit: int = 10) -> List[TestRun]:
        """Get recent test runs"""
        with self.db_manager.get_session() as session:
            return session.query(TestRun).order_by(TestRun.created_at.desc()).limit(limit).all()
    
    def get_test_runs_by_status(self, status: str) -> List[TestRun]:
        """Get test runs by status"""
        with self.db_manager.get_session() as session:
            return session.query(TestRun).filter(TestRun.status == status).all()

class PerformanceMetricRepository:
    """Repository for PerformanceMetric operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def add_metrics(self, metrics_data: List[Dict[str, Any]]) -> List[PerformanceMetric]:
        """Add multiple performance metrics"""
        with self.db_manager.get_session() as session:
            metrics = [PerformanceMetric(**data) for data in metrics_data]
            session.add_all(metrics)
            session.commit()
            return metrics
    
    def get_metrics_by_test_run(self, test_run_id: int) -> List[PerformanceMetric]:
        """Get all metrics for a test run"""
        with self.db_manager.get_session() as session:
            return session.query(PerformanceMetric).filter(
                PerformanceMetric.test_run_id == test_run_id
            ).order_by(PerformanceMetric.timestamp).all()
    
    def get_metrics_by_timerange(self, test_run_id: int, start_time, end_time) -> List[PerformanceMetric]:
        """Get metrics within time range"""
        with self.db_manager.get_session() as session:
            return session.query(PerformanceMetric).filter(
                PerformanceMetric.test_run_id == test_run_id,
                PerformanceMetric.timestamp >= start_time,
                PerformanceMetric.timestamp <= end_time
            ).order_by(PerformanceMetric.timestamp).all()

class LogEntryRepository:
    """Repository for LogEntry operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def add_log_entries(self, log_data: List[Dict[str, Any]]) -> List[LogEntry]:
        """Add multiple log entries"""
        with self.db_manager.get_session() as session:
            logs = [LogEntry(**data) for data in log_data]
            session.add_all(logs)
            session.commit()
            return logs
    
    def get_logs_by_test_run(self, test_run_id: int, log_level: Optional[str] = None) -> List[LogEntry]:
        """Get logs for a test run, optionally filtered by level"""
        with self.db_manager.get_session() as session:
            query = session.query(LogEntry).filter(LogEntry.test_run_id == test_run_id)
            if log_level:
                query = query.filter(LogEntry.log_level == log_level)
            return query.order_by(LogEntry.timestamp).all()
    
    def get_error_logs(self, test_run_id: int) -> List[LogEntry]:
        """Get error logs for a test run"""
        return self.get_logs_by_test_run(test_run_id, 'ERROR')

class AnomalyRepository:
    """Repository for Anomaly operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def add_anomalies(self, anomaly_data: List[Dict[str, Any]]) -> List[Anomaly]:
        """Add multiple anomalies"""
        with self.db_manager.get_session() as session:
            anomalies = [Anomaly(**data) for data in anomaly_data]
            session.add_all(anomalies)
            session.commit()
            return anomalies
    
    def get_anomalies_by_test_run(self, test_run_id: int) -> List[Anomaly]:
        """Get all anomalies for a test run"""
        with self.db_manager.get_session() as session:
            return session.query(Anomaly).filter(
                Anomaly.test_run_id == test_run_id
            ).order_by(Anomaly.timestamp).all()
    
    def get_unresolved_anomalies(self, test_run_id: int) -> List[Anomaly]:
        """Get unresolved anomalies for a test run"""
        with self.db_manager.get_session() as session:
            return session.query(Anomaly).filter(
                Anomaly.test_run_id == test_run_id,
                Anomaly.is_resolved == False
            ).order_by(Anomaly.timestamp).all()

class ReportRepository:
    """Repository for Report operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_report(self, report_data: Dict[str, Any]) -> Report:
        """Create a new report record"""
        with self.db_manager.get_session() as session:
            report = Report(**report_data)
            session.add(report)
            session.commit()
            session.refresh(report)
            return report
    
    def update_report_status(self, report_id: int, status: str, file_path: str = None, error_message: str = None) -> Optional[Report]:
        """Update report status"""
        with self.db_manager.get_session() as session:
            report = session.query(Report).filter(Report.id == report_id).first()
            if report:
                report.status = status
                if file_path:
                    report.file_path = file_path
                if error_message:
                    report.error_message = error_message
                session.commit()
                session.refresh(report)
            return report
    
    def get_reports_by_test_run(self, test_run_id: int) -> List[Report]:
        """Get all reports for a test run"""
        with self.db_manager.get_session() as session:
            return session.query(Report).filter(
                Report.test_run_id == test_run_id
            ).order_by(Report.created_at.desc()).all()

class DatabaseService:
    """High-level database service combining all repositories"""
    
    def __init__(self, database_url: Optional[str] = None):
        self.db_manager = DatabaseManager(database_url)
        self.test_runs = TestRunRepository(self.db_manager)
        self.metrics = PerformanceMetricRepository(self.db_manager)
        self.logs = LogEntryRepository(self.db_manager)
        self.anomalies = AnomalyRepository(self.db_manager)
        self.reports = ReportRepository(self.db_manager)
    
    def initialize_database(self):
        """Initialize database tables"""
        self.db_manager.create_tables()
    
    def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            with self.db_manager.get_session() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        stats = {}
        try:
            with self.db_manager.get_session() as session:
                stats['total_test_runs'] = session.query(TestRun).count()
                stats['completed_test_runs'] = session.query(TestRun).filter(TestRun.status == 'completed').count()
                stats['total_metrics'] = session.query(PerformanceMetric).count()
                stats['total_logs'] = session.query(LogEntry).count()
                stats['total_anomalies'] = session.query(Anomaly).count()
                stats['total_reports'] = session.query(Report).count()
        except Exception as e:
            logger.error(f"Error getting database stats: {str(e)}")
            stats['error'] = str(e)
        
        return stats
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old test data"""
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        try:
            with self.db_manager.get_session() as session:
                # Delete old test runs and related data
                old_test_runs = session.query(TestRun).filter(TestRun.created_at < cutoff_date).all()
                for test_run in old_test_runs:
                    session.delete(test_run)
                session.commit()
                logger.info(f"Cleaned up {len(old_test_runs)} old test runs")
        except Exception as e:
            logger.error(f"Error cleaning up old data: {str(e)}")
    
    def close(self):
        """Close database connections"""
        self.db_manager.close_connections()

# Global database service instance
db_service = None

def get_database_service(database_url: Optional[str] = None) -> DatabaseService:
    """Get or create database service instance"""
    global db_service
    if db_service is None:
        db_service = DatabaseService(database_url)
        db_service.initialize_database()
    return db_service

def init_database(database_url: Optional[str] = None):
    """Initialize database service"""
    global db_service
    db_service = DatabaseService(database_url)
    db_service.initialize_database()
    return db_service