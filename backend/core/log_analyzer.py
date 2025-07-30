"""
Log Analyzer Module
Handles log file parsing and analysis for performance testing
"""

import pandas as pd
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class LogAnalyzer:
    """Analyzes log files to extract performance metrics and error patterns"""
    
    def __init__(self):
        self.log_patterns = {
            'timestamp': r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
            'error': r'(ERROR|Exception|Failed|FATAL)',
            'warning': r'(WARN|Warning)',
            'response_time': r'response_time[:\s]*(\d+\.?\d*)',
            'status_code': r'status[:\s]*(\d{3})',
            'request_id': r'request_id[:\s]*([a-zA-Z0-9-]+)',
            'endpoint': r'(GET|POST|PUT|DELETE)\s+([^\s]+)',
            'ip_address': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        }
        self.parsed_logs = []
        
    def parse_log_file(self, file_path: str) -> pd.DataFrame:
        """
        Parse log file and extract structured data
        
        Args:
            file_path: Path to the log file
            
        Returns:
            pd.DataFrame: Parsed log data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            parsed_data = []
            
            for line_num, line in enumerate(lines, 1):
                parsed_line = self._parse_line(line.strip(), line_num)
                if parsed_line:
                    parsed_data.append(parsed_line)
            
            df = pd.DataFrame(parsed_data)
            logger.info(f"Successfully parsed {len(df)} log entries from {file_path}")
            return df
            
        except Exception as e:
            logger.error(f"Error parsing log file {file_path}: {str(e)}")
            raise
    
    def _parse_line(self, line: str, line_num: int) -> Optional[Dict]:
        """
        Parse individual log line
        
        Args:
            line: Log line to parse
            line_num: Line number for reference
            
        Returns:
            Dict: Parsed log entry or None if parsing fails
        """
        try:
            parsed = {
                'line_number': line_num,
                'raw_line': line,
                'timestamp': None,
                'log_level': None,
                'message': line,
                'response_time': None,
                'status_code': None,
                'request_id': None,
                'endpoint': None,
                'ip_address': None
            }
            
            # Extract timestamp
            timestamp_match = re.search(self.log_patterns['timestamp'], line)
            if timestamp_match:
                parsed['timestamp'] = timestamp_match.group(1)
            
            # Extract log level
            if re.search(self.log_patterns['error'], line, re.IGNORECASE):
                parsed['log_level'] = 'ERROR'
            elif re.search(self.log_patterns['warning'], line, re.IGNORECASE):
                parsed['log_level'] = 'WARN'
            else:
                parsed['log_level'] = 'INFO'
            
            # Extract response time
            response_time_match = re.search(self.log_patterns['response_time'], line)
            if response_time_match:
                parsed['response_time'] = float(response_time_match.group(1))
            
            # Extract status code
            status_match = re.search(self.log_patterns['status_code'], line)
            if status_match:
                parsed['status_code'] = int(status_match.group(1))
            
            # Extract request ID
            request_id_match = re.search(self.log_patterns['request_id'], line)
            if request_id_match:
                parsed['request_id'] = request_id_match.group(1)
            
            # Extract endpoint
            endpoint_match = re.search(self.log_patterns['endpoint'], line)
            if endpoint_match:
                parsed['endpoint'] = endpoint_match.group(2)
            
            # Extract IP address
            ip_match = re.search(self.log_patterns['ip_address'], line)
            if ip_match:
                parsed['ip_address'] = ip_match.group(1)
            
            return parsed
            
        except Exception as e:
            logger.warning(f"Failed to parse line {line_num}: {str(e)}")
            return None
    
    def analyze_error_patterns(self, df: pd.DataFrame) -> Dict:
        """
        Analyze error patterns in log data
        
        Args:
            df: Parsed log DataFrame
            
        Returns:
            Dict: Error analysis results
        """
        if df.empty:
            return {}
        
        error_analysis = {
            'total_entries': len(df),
            'error_count': len(df[df['log_level'] == 'ERROR']),
            'warning_count': len(df[df['log_level'] == 'WARN']),
            'error_rate': 0.0,
            'top_errors': [],
            'error_timeline': [],
            'status_code_distribution': {}
        }
        
        # Calculate error rate
        if error_analysis['total_entries'] > 0:
            error_analysis['error_rate'] = (
                error_analysis['error_count'] / error_analysis['total_entries'] * 100
            )
        
        # Top error messages
        error_messages = df[df['log_level'] == 'ERROR']['message'].value_counts().head(10)
        error_analysis['top_errors'] = [
            {'message': msg, 'count': count} 
            for msg, count in error_messages.items()
        ]
        
        # Status code distribution
        if 'status_code' in df.columns:
            status_counts = df['status_code'].value_counts()
            error_analysis['status_code_distribution'] = status_counts.to_dict()
        
        return error_analysis
    
    def analyze_performance_patterns(self, df: pd.DataFrame) -> Dict:
        """
        Analyze performance patterns in log data
        
        Args:
            df: Parsed log DataFrame
            
        Returns:
            Dict: Performance analysis results
        """
        if df.empty:
            return {}
        
        performance_analysis = {
            'response_time_stats': {},
            'throughput_analysis': {},
            'endpoint_performance': {},
            'time_based_analysis': {}
        }
        
        # Response time statistics
        if 'response_time' in df.columns:
            response_times = df['response_time'].dropna()
            if not response_times.empty:
                performance_analysis['response_time_stats'] = {
                    'min': float(response_times.min()),
                    'max': float(response_times.max()),
                    'mean': float(response_times.mean()),
                    'median': float(response_times.median()),
                    'std': float(response_times.std()),
                    'p90': float(response_times.quantile(0.9)),
                    'p95': float(response_times.quantile(0.95)),
                    'p99': float(response_times.quantile(0.99))
                }
        
        # Endpoint performance
        if 'endpoint' in df.columns:
            endpoint_stats = df.groupby('endpoint')['response_time'].agg([
                'count', 'mean', 'min', 'max', 'std'
            ]).round(2)
            performance_analysis['endpoint_performance'] = endpoint_stats.to_dict('index')
        
        return performance_analysis
    
    def detect_anomalies(self, df: pd.DataFrame, column: str = 'response_time', 
                        threshold: float = 2.0) -> List[Dict]:
        """
        Detect anomalies in log data
        
        Args:
            df: Parsed log DataFrame
            column: Column to analyze for anomalies
            threshold: Standard deviation threshold
            
        Returns:
            List[Dict]: Detected anomalies
        """
        if df.empty or column not in df.columns:
            return []
        
        data = df[column].dropna()
        if data.empty:
            return []
        
        mean = data.mean()
        std = data.std()
        
        if std == 0:
            return []
        
        # Detect outliers using z-score
        z_scores = abs((data - mean) / std)
        anomalies = data[z_scores > threshold]
        
        anomaly_list = []
        for idx, value in anomalies.items():
            anomaly_list.append({
                'line_number': int(df.iloc[idx]['line_number']),
                'value': float(value),
                'z_score': float(z_scores[idx]),
                'timestamp': df.iloc[idx].get('timestamp'),
                'message': df.iloc[idx].get('message', '')
            })
        
        return anomaly_list
    
    def generate_log_summary(self, df: pd.DataFrame) -> Dict:
        """
        Generate comprehensive log summary
        
        Args:
            df: Parsed log DataFrame
            
        Returns:
            Dict: Log summary
        """
        if df.empty:
            return {}
        
        summary = {
            'total_entries': len(df),
            'time_range': {},
            'log_level_distribution': {},
            'unique_endpoints': 0,
            'unique_ips': 0,
            'data_quality': {}
        }
        
        # Time range
        if 'timestamp' in df.columns:
            timestamps = pd.to_datetime(df['timestamp'], errors='coerce').dropna()
            if not timestamps.empty:
                summary['time_range'] = {
                    'start': timestamps.min().isoformat(),
                    'end': timestamps.max().isoformat(),
                    'duration_hours': (timestamps.max() - timestamps.min()).total_seconds() / 3600
                }
        
        # Log level distribution
        if 'log_level' in df.columns:
            level_counts = df['log_level'].value_counts()
            summary['log_level_distribution'] = level_counts.to_dict()
        
        # Unique counts
        if 'endpoint' in df.columns:
            summary['unique_endpoints'] = df['endpoint'].nunique()
        
        if 'ip_address' in df.columns:
            summary['unique_ips'] = df['ip_address'].nunique()
        
        # Data quality
        missing_data = df.isnull().sum()
        summary['data_quality'] = {
            'missing_values': missing_data.to_dict(),
            'completeness_rate': (1 - missing_data.sum() / (len(df) * len(df.columns))) * 100
        }
        
        return summary