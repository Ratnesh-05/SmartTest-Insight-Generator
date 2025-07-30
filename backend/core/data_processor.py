"""
Data Processor Module
Handles performance test data processing using Pandas and NumPy
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PerformanceDataProcessor:
    """Processes performance test data and calculates key metrics"""
    
    def __init__(self):
        self.df = None
        self.metrics = {}
        
    def load_test_data(self, file_path: str, file_type: str = 'auto') -> pd.DataFrame:
        """
        Load performance test data from various file formats
        
        Args:
            file_path: Path to the data file
            file_type: Type of file ('csv', 'excel', 'json', 'auto')
            
        Returns:
            pd.DataFrame: Loaded data
        """
        try:
            if file_type == 'auto':
                if file_path.endswith('.csv'):
                    self.df = pd.read_csv(file_path)
                elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                    self.df = pd.read_excel(file_path)
                elif file_path.endswith('.json'):
                    self.df = pd.read_json(file_path)
                else:
                    raise ValueError(f"Unsupported file type: {file_path}")
            else:
                if file_type == 'csv':
                    self.df = pd.read_csv(file_path)
                elif file_type == 'excel':
                    self.df = pd.read_excel(file_path)
                elif file_type == 'json':
                    self.df = pd.read_json(file_path)
                else:
                    raise ValueError(f"Unsupported file type: {file_type}")
            
            logger.info(f"Successfully loaded data from {file_path}")
            return self.df
            
        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {str(e)}")
            raise
    
    def calculate_basic_metrics(self) -> Dict:
        """
        Calculate basic performance metrics
        
        Returns:
            Dict: Dictionary containing calculated metrics
        """
        if self.df is None:
            raise ValueError("No data loaded. Please load data first.")
        
        metrics = {}
        
        # Response time metrics
        if 'response_time' in self.df.columns:
            response_times = self.df['response_time']
            metrics['response_time'] = {
                'min': float(response_times.min()),
                'max': float(response_times.max()),
                'mean': float(response_times.mean()),
                'median': float(response_times.median()),
                'std': float(response_times.std()),
                'p50': float(response_times.quantile(0.5)),
                'p90': float(response_times.quantile(0.9)),
                'p95': float(response_times.quantile(0.95)),
                'p99': float(response_times.quantile(0.99))
            }
        
        # Throughput metrics
        if 'requests_per_sec' in self.df.columns:
            throughput = self.df['requests_per_sec']
            metrics['throughput'] = {
                'min': float(throughput.min()),
                'max': float(throughput.max()),
                'mean': float(throughput.mean()),
                'total_requests': int(throughput.sum())
            }
        
        # Error metrics
        if 'status_code' in self.df.columns:
            total_requests = len(self.df)
            error_requests = len(self.df[self.df['status_code'] >= 400])
            metrics['errors'] = {
                'total_requests': total_requests,
                'error_requests': error_requests,
                'error_rate': float(error_requests / total_requests * 100) if total_requests > 0 else 0.0
            }
        
        # Concurrent users
        if 'concurrent_users' in self.df.columns:
            metrics['concurrent_users'] = {
                'max': int(self.df['concurrent_users'].max()),
                'avg': float(self.df['concurrent_users'].mean())
            }
        
        self.metrics = metrics
        return metrics
    
    def detect_anomalies(self, column: str = 'response_time', threshold: float = 2.0) -> List[Dict]:
        """
        Detect anomalies using statistical methods
        
        Args:
            column: Column to analyze for anomalies
            threshold: Standard deviation threshold for anomaly detection
            
        Returns:
            List[Dict]: List of detected anomalies
        """
        if self.df is None or column not in self.df.columns:
            return []
        
        data = self.df[column].dropna()
        mean = data.mean()
        std = data.std()
        
        # Detect outliers using z-score
        z_scores = np.abs((data - mean) / std)
        anomalies = data[z_scores > threshold]
        
        anomaly_list = []
        for idx, value in anomalies.items():
            anomaly_list.append({
                'index': int(idx),
                'value': float(value),
                'z_score': float(z_scores[idx]),
                'timestamp': self.df.iloc[idx].get('timestamp', None)
            })
        
        return anomaly_list
    
    def get_data_summary(self) -> Dict:
        """
        Get comprehensive data summary
        
        Returns:
            Dict: Data summary including shape, columns, data types
        """
        if self.df is None:
            return {}
        
        return {
            'shape': self.df.shape,
            'columns': list(self.df.columns),
            'data_types': self.df.dtypes.to_dict(),
            'missing_values': self.df.isnull().sum().to_dict(),
            'memory_usage': self.df.memory_usage(deep=True).sum()
        }
    
    def filter_data(self, filters: Dict) -> pd.DataFrame:
        """
        Filter data based on conditions
        
        Args:
            filters: Dictionary of column: condition pairs
            
        Returns:
            pd.DataFrame: Filtered data
        """
        if self.df is None:
            return pd.DataFrame()
        
        filtered_df = self.df.copy()
        
        for column, condition in filters.items():
            if column in filtered_df.columns:
                if isinstance(condition, (list, tuple)):
                    filtered_df = filtered_df[filtered_df[column].isin(condition)]
                elif isinstance(condition, dict):
                    if 'min' in condition:
                        filtered_df = filtered_df[filtered_df[column] >= condition['min']]
                    if 'max' in condition:
                        filtered_df = filtered_df[filtered_df[column] <= condition['max']]
                else:
                    filtered_df = filtered_df[filtered_df[column] == condition]
        
        return filtered_df