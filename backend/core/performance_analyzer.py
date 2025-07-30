"""
Performance Analyzer Module
Advanced performance analysis using Scikit-learn for ML insights
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class PerformanceAnalyzer:
    """Advanced performance analysis with machine learning capabilities"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.clusterer = KMeans(n_clusters=3, random_state=42)
        
    def analyze_performance_trends(self, df: pd.DataFrame) -> Dict:
        """
        Analyze performance trends over time
        
        Args:
            df: DataFrame with performance data
            
        Returns:
            Dict: Trend analysis results
        """
        if df.empty:
            return {}
            
        trends = {
            'response_time_trend': {},
            'throughput_trend': {},
            'error_rate_trend': {},
            'seasonal_patterns': {},
            'recommendations': []
        }
        
        # Response time trend analysis
        if 'response_time' in df.columns and 'timestamp' in df.columns:
            df_time = df.copy()
            df_time['timestamp'] = pd.to_datetime(df_time['timestamp'], errors='coerce')
            df_time = df_time.dropna(subset=['timestamp', 'response_time'])
            
            if not df_time.empty:
                df_time = df_time.sort_values('timestamp')
                df_time['hour'] = df_time['timestamp'].dt.hour
                df_time['day_of_week'] = df_time['timestamp'].dt.dayofweek
                
                # Hourly patterns
                hourly_avg = df_time.groupby('hour')['response_time'].mean()
                trends['response_time_trend']['hourly_pattern'] = hourly_avg.to_dict()
                
                # Daily patterns
                daily_avg = df_time.groupby('day_of_week')['response_time'].mean()
                trends['response_time_trend']['daily_pattern'] = daily_avg.to_dict()
                
                # Trend direction
                if len(df_time) > 1:
                    correlation = np.corrcoef(range(len(df_time)), df_time['response_time'])[0, 1]
                    trends['response_time_trend']['trend_direction'] = 'increasing' if correlation > 0.1 else 'decreasing' if correlation < -0.1 else 'stable'
        
        return trends
    
    def detect_performance_anomalies(self, df: pd.DataFrame) -> Dict:
        """
        Detect performance anomalies using machine learning
        
        Args:
            df: DataFrame with performance metrics
            
        Returns:
            Dict: Anomaly detection results
        """
        if df.empty:
            return {}
            
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            return {}
            
        # Prepare data for ML
        ml_data = df[numeric_cols].fillna(df[numeric_cols].median())
        
        if len(ml_data) < 10:  # Need minimum data for ML
            return {'error': 'Insufficient data for ML analysis'}
            
        # Scale the data
        scaled_data = self.scaler.fit_transform(ml_data)
        
        # Detect anomalies
        anomaly_labels = self.anomaly_detector.fit_predict(scaled_data)
        
        # Find anomalous records
        anomalies = df[anomaly_labels == -1].copy()
        
        results = {
            'total_records': len(df),
            'anomaly_count': len(anomalies),
            'anomaly_percentage': (len(anomalies) / len(df)) * 100,
            'anomaly_indices': anomalies.index.tolist(),
            'anomaly_summary': {}
        }
        
        # Analyze anomaly characteristics
        if not anomalies.empty:
            for col in numeric_cols:
                if col in anomalies.columns:
                    results['anomaly_summary'][col] = {
                        'mean': float(anomalies[col].mean()),
                        'std': float(anomalies[col].std()),
                        'min': float(anomalies[col].min()),
                        'max': float(anomalies[col].max())
                    }
        
        return results
    
    def cluster_performance_patterns(self, df: pd.DataFrame) -> Dict:
        """
        Cluster performance data to identify patterns
        
        Args:
            df: DataFrame with performance data
            
        Returns:
            Dict: Clustering results
        """
        if df.empty:
            return {}
            
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            return {}
            
        ml_data = df[numeric_cols].fillna(df[numeric_cols].median())
        
        if len(ml_data) < 10:
            return {'error': 'Insufficient data for clustering'}
            
        # Scale and cluster
        scaled_data = self.scaler.fit_transform(ml_data)
        cluster_labels = self.clusterer.fit_predict(scaled_data)
        
        # Analyze clusters
        df_clustered = df.copy()
        df_clustered['cluster'] = cluster_labels
        
        cluster_analysis = {
            'n_clusters': self.clusterer.n_clusters,
            'cluster_summary': {},
            'cluster_characteristics': {}
        }
        
        for cluster_id in range(self.clusterer.n_clusters):
            cluster_data = df_clustered[df_clustered['cluster'] == cluster_id]
            
            cluster_analysis['cluster_summary'][f'cluster_{cluster_id}'] = {
                'size': len(cluster_data),
                'percentage': (len(cluster_data) / len(df)) * 100
            }
            
            # Analyze cluster characteristics
            cluster_chars = {}
            for col in numeric_cols:
                if col in cluster_data.columns:
                    cluster_chars[col] = {
                        'mean': float(cluster_data[col].mean()),
                        'std': float(cluster_data[col].std())
                    }
            cluster_analysis['cluster_characteristics'][f'cluster_{cluster_id}'] = cluster_chars
        
        return cluster_analysis
    
    def predict_performance_degradation(self, df: pd.DataFrame) -> Dict:
        """
        Predict potential performance degradation
        
        Args:
            df: DataFrame with time-series performance data
            
        Returns:
            Dict: Prediction results
        """
        if df.empty or 'timestamp' not in df.columns:
            return {}
            
        # Prepare time series data
        df_ts = df.copy()
        df_ts['timestamp'] = pd.to_datetime(df_ts['timestamp'], errors='coerce')
        df_ts = df_ts.dropna(subset=['timestamp']).sort_values('timestamp')
        
        if len(df_ts) < 20:  # Need sufficient history
            return {'error': 'Insufficient historical data for prediction'}
            
        predictions = {
            'trend_analysis': {},
            'risk_assessment': {},
            'recommendations': []
        }
        
        # Analyze response time trends
        if 'response_time' in df_ts.columns:
            rt_data = df_ts['response_time'].dropna()
            if len(rt_data) > 10:
                # Simple trend analysis
                x = np.arange(len(rt_data))
                correlation = np.corrcoef(x, rt_data)[0, 1]
                
                predictions['trend_analysis']['response_time'] = {
                    'trend_strength': abs(correlation),
                    'trend_direction': 'increasing' if correlation > 0 else 'decreasing',
                    'risk_level': 'high' if correlation > 0.3 else 'medium' if correlation > 0.1 else 'low'
                }
                
                # Generate recommendations
                if correlation > 0.3:
                    predictions['recommendations'].append("Response time is increasing significantly. Consider performance optimization.")
                elif correlation > 0.1:
                    predictions['recommendations'].append("Response time shows slight increase. Monitor closely.")
        
        # Analyze error rate trends
        if 'error_rate' in df_ts.columns:
            error_data = df_ts['error_rate'].dropna()
            if len(error_data) > 10:
                x = np.arange(len(error_data))
                correlation = np.corrcoef(x, error_data)[0, 1]
                
                predictions['trend_analysis']['error_rate'] = {
                    'trend_strength': abs(correlation),
                    'trend_direction': 'increasing' if correlation > 0 else 'decreasing',
                    'risk_level': 'high' if correlation > 0.2 else 'medium' if correlation > 0.05 else 'low'
                }
        
        return predictions
    
    def generate_performance_insights(self, df: pd.DataFrame) -> Dict:
        """
        Generate comprehensive performance insights
        
        Args:
            df: DataFrame with performance data
            
        Returns:
            Dict: Performance insights
        """
        insights = {
            'summary': {},
            'key_findings': [],
            'recommendations': [],
            'risk_areas': []
        }
        
        if df.empty:
            return insights
            
        # Basic statistics
        if 'response_time' in df.columns:
            rt = df['response_time'].dropna()
            if not rt.empty:
                insights['summary']['response_time'] = {
                    'avg': float(rt.mean()),
                    'p95': float(rt.quantile(0.95)),
                    'p99': float(rt.quantile(0.99)),
                    'variability': float(rt.std() / rt.mean()) if rt.mean() > 0 else 0
                }
                
                # Generate insights
                if rt.quantile(0.95) > rt.mean() * 3:
                    insights['key_findings'].append("High response time variability detected")
                    insights['recommendations'].append("Investigate causes of response time spikes")
                
                if rt.mean() > 1000:  # Assuming milliseconds
                    insights['risk_areas'].append("Average response time exceeds 1 second")
        
        # Throughput analysis
        if 'throughput' in df.columns:
            tp = df['throughput'].dropna()
            if not tp.empty:
                insights['summary']['throughput'] = {
                    'avg': float(tp.mean()),
                    'max': float(tp.max()),
                    'stability': float(1 - (tp.std() / tp.mean())) if tp.mean() > 0 else 0
                }
        
        # Error analysis
        if 'error_rate' in df.columns:
            er = df['error_rate'].dropna()
            if not er.empty:
                avg_error_rate = er.mean()
                insights['summary']['error_rate'] = {
                    'avg': float(avg_error_rate),
                    'max': float(er.max())
                }
                
                if avg_error_rate > 5:  # 5% error rate
                    insights['risk_areas'].append("High error rate detected")
                    insights['recommendations'].append("Investigate and fix error causes")
        
        return insights