"""
Configuration Module
Application settings and configuration management
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path

class Config:
    """Application configuration class"""
    
    # Base directory
    BASE_DIR = Path(__file__).parent
    
    # Database configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///smarttest_insights.db')
    
    # File paths
    DATA_DIR = BASE_DIR / 'data'
    LOGS_DIR = DATA_DIR / 'logs'
    REPORTS_DIR = DATA_DIR / 'reports'
    TEST_DATA_DIR = DATA_DIR / 'test_data'
    
    # Create directories if they don't exist
    for dir_path in [DATA_DIR, LOGS_DIR, REPORTS_DIR, TEST_DATA_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Performance thresholds
    THRESHOLDS = {
        'response_time': {
            'warning': 1000,  # ms
            'critical': 3000   # ms
        },
        'error_rate': {
            'warning': 5.0,    # %
            'critical': 10.0   # %
        },
        'throughput': {
            'warning': 100,    # req/sec
            'critical': 50     # req/sec
        }
    }
    
    # Report settings
    REPORT_SETTINGS = {
        'default_format': 'pdf',
        'output_dir': str(REPORTS_DIR),
        'templates_dir': str(BASE_DIR / 'backend' / 'reports'),
        'max_file_size': 50 * 1024 * 1024,  # 50MB
        'retention_days': 30
    }
    
    # Logging configuration
    LOGGING = {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': str(LOGS_DIR / 'smarttest_insights.log'),
        'max_size': 10 * 1024 * 1024,  # 10MB
        'backup_count': 5
    }
    
    # ML/Analytics settings
    ML_SETTINGS = {
        'anomaly_detection': {
            'contamination': 0.1,
            'random_state': 42
        },
        'clustering': {
            'n_clusters': 3,
            'random_state': 42
        },
        'prediction': {
            'min_data_points': 20,
            'confidence_threshold': 0.8
        }
    }
    
    # Email settings (optional)
    EMAIL_SETTINGS = {
        'enabled': False,
        'smtp_server': os.getenv('SMTP_SERVER', ''),
        'smtp_port': int(os.getenv('SMTP_PORT', '587')),
        'username': os.getenv('EMAIL_USERNAME', ''),
        'password': os.getenv('EMAIL_PASSWORD', ''),
        'from_email': os.getenv('FROM_EMAIL', ''),
        'to_emails': os.getenv('TO_EMAILS', '').split(',') if os.getenv('TO_EMAILS') else []
    }
    
    # Security settings
    SECURITY = {
        'secret_key': os.getenv('SECRET_KEY', 'your-secret-key-change-in-production'),
        'session_timeout': 3600,  # 1 hour
        'max_file_upload_size': 100 * 1024 * 1024  # 100MB
    }
    
    # Development settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    TESTING = os.getenv('TESTING', 'False').lower() == 'true'
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get database URL with fallback"""
        return cls.DATABASE_URL
    
    @classmethod
    def get_threshold(cls, metric: str, level: str = 'warning') -> float:
        """Get threshold value for a metric"""
        return cls.THRESHOLDS.get(metric, {}).get(level, 0.0)
    
    @classmethod
    def get_report_path(cls, filename: str) -> str:
        """Get full path for report file"""
        return str(cls.REPORTS_DIR / filename)
    
    @classmethod
    def get_log_path(cls) -> str:
        """Get log file path"""
        return cls.LOGGING['file']
    
    @classmethod
    def is_email_enabled(cls) -> bool:
        """Check if email notifications are enabled"""
        return cls.EMAIL_SETTINGS['enabled'] and all([
            cls.EMAIL_SETTINGS['smtp_server'],
            cls.EMAIL_SETTINGS['username'],
            cls.EMAIL_SETTINGS['password']
        ])

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOGGING = {
        'level': 'DEBUG',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': str(Config.LOGS_DIR / 'smarttest_insights_dev.log'),
        'max_size': 5 * 1024 * 1024,  # 5MB
        'backup_count': 3
    }

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///smarttest_insights_prod.db')
    
    # Stricter thresholds for production
    THRESHOLDS = {
        'response_time': {
            'warning': 800,   # ms
            'critical': 2000  # ms
        },
        'error_rate': {
            'warning': 3.0,   # %
            'critical': 7.0   # %
        },
        'throughput': {
            'warning': 150,   # req/sec
            'critical': 75    # req/sec
        }
    }

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'  # In-memory database for testing
    LOGGING = {
        'level': 'WARNING',
        'format': '%(levelname)s - %(message)s',
        'file': None,  # No file logging for tests
        'max_size': 1024 * 1024,
        'backup_count': 1
    }

# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': Config
}

def get_config(config_name: Optional[str] = None) -> Config:
    """
    Get configuration instance
    
    Args:
        config_name: Configuration name (development, production, testing)
        
    Returns:
        Config: Configuration instance
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    
    config_class = config_map.get(config_name, Config)
    return config_class()

# Global configuration instance
config = get_config() 