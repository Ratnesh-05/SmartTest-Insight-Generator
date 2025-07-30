"""
ML Insights Module
Machine learning-powered insights for performance testing
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class MLInsights:
    """Machine learning insights for performance analysis"""
    
    def __init__(self):
        self.response_time_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.throughput_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.label_encoders = {}
        self.is_trained = False
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for machine learning
        
        Args:
            df: Raw DataFrame
            
        Returns:
            pd.DataFrame: Prepared features
        """
        if df.empty:
            return pd.DataFrame()
            
        features_df = df.copy()
        
        # Handle timestamp features
        if 'timestamp' in features_df.columns:
            features_df['timestamp'] = pd.to_datetime(features_df['timestamp'], errors='coerce')
            features_df['hour'] = features_df['timestamp'].dt.hour
            features_df['day_of_week'] = features_df['timestamp'].dt.dayofweek
            features_df['minute'] = features_df['timestamp'].dt.minute
            features_df.drop('timestamp', axis=1, inplace=True)
        
        # Encode categorical variables
        categorical_cols = features_df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                features_df[col] = self.label_encoders[col].fit_transform(features_df[col].astype(str))
            else:
                # Handle unseen categories
                try:
                    features_df[col] = self.label_encoders[col].transform(features_df[col].astype(str))
                except ValueError:
                    # For unseen categories, assign -1
                    features_df[col] = features_df[col].apply(
                        lambda x: self.label_encoders[col].transform([str(x)])[0] 
                        if str(x) in self.label_encoders[col].classes_ else -1
                    )
        
        # Fill missing values
        numeric_cols = features_df.select_dtypes(include=[np.number]).columns
        features_df[numeric_cols] = features_df[numeric_cols].fillna(features_df[numeric_cols].median())
        
        return features_df
    
    def train_models(self, df: pd.DataFrame) -> Dict:
        """
        Train ML models for predictions
        
        Args:
            df: Training data
            
        Returns:
            Dict: Training results
        """
        if df.empty:
            return {'error': 'No data provided for training'}
            
        # Prepare features
        features_df = self.prepare_features(df)
        
        if len(features_df) < 50:
            return {'error': 'Insufficient data for training (minimum 50 records required)'}
        
        training_results = {
            'response_time_model': {},
            'throughput_model': {},
            'feature_importance': {}
        }
        
        # Train response time model
        if 'response_time' in features_df.columns:
            target_col = 'response_time'
            feature_cols = [col for col in features_df.columns if col != target_col]
            
            if len(feature_cols) > 0:
                X = features_df[feature_cols]
                y = features_df[target_col]
                
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                
                self.response_time_model.fit(X_train, y_train)
                y_pred = self.response_time_model.predict(X_test)
                
                training_results['response_time_model'] = {
                    'mse': float(mean_squared_error(y_test, y_pred)),
                    'r2_score': float(r2_score(y_test, y_pred)),
                    'feature_count': len(feature_cols)
                }
                
                # Feature importance
                importance = self.response_time_model.feature_importances_
                feature_importance = dict(zip(feature_cols, importance))
                training_results['feature_importance']['response_time'] = feature_importance
        
        # Train throughput model
        if 'throughput' in features_df.columns:
            target_col = 'throughput'
            feature_cols = [col for col in features_df.columns if col != target_col and col != 'response_time']
            
            if len(feature_cols) > 0:
                X = features_df[feature_cols]
                y = features_df[target_col]
                
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                
                self.throughput_model.fit(X_train, y_train)
                y_pred = self.throughput_model.predict(X_test)
                
                training_results['throughput_model'] = {
                    'mse': float(mean_squared_error(y_test, y_pred)),
                    'r2_score': float(r2_score(y_test, y_pred)),
                    'feature_count': len(feature_cols)
                }
                
                # Feature importance
                importance = self.throughput_model.feature_importances_
                feature_importance = dict(zip(feature_cols, importance))
                training_results['feature_importance']['throughput'] = feature_importance
        
        self.is_trained = True
        return training_results
    
    def predict_performance(self, scenarios: List[Dict]) -> Dict:
        """
        Predict performance for given scenarios
        
        Args:
            scenarios: List of scenario dictionaries
            
        Returns:
            Dict: Predictions
        """
        if not self.is_trained:
            return {'error': 'Models not trained. Call train_models() first.'}
        
        if not scenarios:
            return {'error': 'No scenarios provided'}
        
        predictions = {
            'scenarios': [],
            'summary': {}
        }
        
        # Convert scenarios to DataFrame
        scenarios_df = pd.DataFrame(scenarios)
        features_df = self.prepare_features(scenarios_df)
        
        for i, scenario in enumerate(scenarios):
            scenario_pred = {
                'scenario_id': i,
                'input': scenario,
                'predictions': {}
            }
            
            # Predict response time
            try:
                rt_pred = self.response_time_model.predict(features_df.iloc[[i]])[0]
                scenario_pred['predictions']['response_time'] = float(rt_pred)
            except Exception as e:
                scenario_pred['predictions']['response_time'] = None
                logger.warning(f"Response time prediction failed: {e}")
            
            # Predict throughput
            try:
                tp_pred = self.throughput_model.predict(features_df.iloc[[i]])[0]
                scenario_pred['predictions']['throughput'] = float(tp_pred)
            except Exception as e:
                scenario_pred['predictions']['throughput'] = None
                logger.warning(f"Throughput prediction failed: {e}")
            
            predictions['scenarios'].append(scenario_pred)
        
        # Calculate summary statistics
        response_times = [s['predictions']['response_time'] for s in predictions['scenarios'] 
                         if s['predictions']['response_time'] is not None]
        throughputs = [s['predictions']['throughput'] for s in predictions['scenarios'] 
                      if s['predictions']['throughput'] is not None]
        
        if response_times:
            predictions['summary']['response_time'] = {
                'min': float(min(response_times)),
                'max': float(max(response_times)),
                'avg': float(np.mean(response_times))
            }
        
        if throughputs:
            predictions['summary']['throughput'] = {
                'min': float(min(throughputs)),
                'max': float(max(throughputs)),
                'avg': float(np.mean(throughputs))
            }
        
        return predictions
    
    def identify_performance_bottlenecks(self, df: pd.DataFrame) -> Dict:
        """
        Identify performance bottlenecks using ML analysis
        
        Args:
            df: Performance data
            
        Returns:
            Dict: Bottleneck analysis
        """
        if df.empty:
            return {}
        
        bottlenecks = {
            'resource_constraints': [],
            'timing_issues': [],
            'scaling_problems': [],
            'recommendations': []
        }
        
        # Analyze concurrent users vs performance
        if 'concurrent_users' in df.columns and 'response_time' in df.columns:
            correlation = df['concurrent_users'].corr(df['response_time'])
            if correlation > 0.7:
                bottlenecks['scaling_problems'].append({
                    'issue': 'Strong correlation between concurrent users and response time',
                    'correlation': float(correlation),
                    'severity': 'high'
                })
                bottlenecks['recommendations'].append('Consider horizontal scaling or load balancing')
        
        # Analyze memory usage patterns
        if 'memory_usage' in df.columns and 'response_time' in df.columns:
            correlation = df['memory_usage'].corr(df['response_time'])
            if correlation > 0.6:
                bottlenecks['resource_constraints'].append({
                    'issue': 'Memory usage affecting response time',
                    'correlation': float(correlation),
                    'severity': 'medium'
                })
                bottlenecks['recommendations'].append('Optimize memory usage or increase memory allocation')
        
        # Analyze CPU patterns
        if 'cpu_usage' in df.columns and 'response_time' in df.columns:
            correlation = df['cpu_usage'].corr(df['response_time'])
            if correlation > 0.6:
                bottlenecks['resource_constraints'].append({
                    'issue': 'CPU usage affecting response time',
                    'correlation': float(correlation),
                    'severity': 'high'
                })
                bottlenecks['recommendations'].append('Optimize CPU-intensive operations or scale compute resources')
        
        # Analyze time-based patterns
        if 'timestamp' in df.columns and 'response_time' in df.columns:
            df_time = df.copy()
            df_time['timestamp'] = pd.to_datetime(df_time['timestamp'], errors='coerce')
            df_time['hour'] = df_time['timestamp'].dt.hour
            
            hourly_stats = df_time.groupby('hour')['response_time'].agg(['mean', 'std'])
            peak_hours = hourly_stats[hourly_stats['mean'] > hourly_stats['mean'].quantile(0.8)]
            
            if len(peak_hours) > 0:
                bottlenecks['timing_issues'].append({
                    'issue': 'Performance degradation during peak hours',
                    'peak_hours': peak_hours.index.tolist(),
                    'severity': 'medium'
                })
                bottlenecks['recommendations'].append('Consider auto-scaling during peak hours')
        
        return bottlenecks
    
    def generate_capacity_recommendations(self, df: pd.DataFrame, target_metrics: Dict) -> Dict:
        """
        Generate capacity planning recommendations
        
        Args:
            df: Historical performance data
            target_metrics: Target performance metrics
            
        Returns:
            Dict: Capacity recommendations
        """
        if df.empty:
            return {}
        
        recommendations = {
            'current_capacity': {},
            'target_capacity': {},
            'scaling_recommendations': [],
            'cost_analysis': {}
        }
        
        # Analyze current capacity
        if 'concurrent_users' in df.columns:
            max_users = df['concurrent_users'].max()
            avg_users = df['concurrent_users'].mean()
            
            recommendations['current_capacity'] = {
                'max_concurrent_users': int(max_users),
                'avg_concurrent_users': float(avg_users),
                'peak_utilization': float(max_users / avg_users) if avg_users > 0 else 0
            }
        
        # Calculate target capacity based on performance requirements
        target_response_time = target_metrics.get('response_time', 1000)  # Default 1 second
        target_throughput = target_metrics.get('throughput', 100)  # Default 100 RPS
        
        # Find optimal user load for target performance
        if 'response_time' in df.columns and 'concurrent_users' in df.columns:
            acceptable_data = df[df['response_time'] <= target_response_time]
            
            if not acceptable_data.empty:
                optimal_users = acceptable_data['concurrent_users'].max()
                recommendations['target_capacity']['optimal_concurrent_users'] = int(optimal_users)
                
                current_max = recommendations['current_capacity'].get('max_concurrent_users', 0)
                if optimal_users < current_max:
                    scaling_factor = current_max / optimal_users
                    recommendations['scaling_recommendations'].append({
                        'type': 'scale_up',
                        'factor': float(scaling_factor),
                        'reason': f'Current load exceeds optimal capacity by {scaling_factor:.1f}x'
                    })
        
        # Throughput analysis
        if 'throughput' in df.columns:
            current_max_throughput = df['throughput'].max()
            if current_max_throughput < target_throughput:
                throughput_gap = target_throughput / current_max_throughput
                recommendations['scaling_recommendations'].append({
                    'type': 'increase_throughput',
                    'factor': float(throughput_gap),
                    'reason': f'Need {throughput_gap:.1f}x throughput increase to meet targets'
                })
        
        return recommendations
    
    def analyze_feature_impact(self, df: pd.DataFrame) -> Dict:
        """
        Analyze impact of different features on performance
        
        Args:
            df: Performance data with features
            
        Returns:
            Dict: Feature impact analysis
        """
        if not self.is_trained or df.empty:
            return {}
        
        feature_analysis = {
            'response_time_drivers': {},
            'throughput_drivers': {},
            'actionable_insights': []
        }
        
        # Get feature importance from trained models
        if hasattr(self.response_time_model, 'feature_importances_'):
            feature_names = [col for col in df.columns if col != 'response_time']
            importance_scores = self.response_time_model.feature_importances_
            
            feature_analysis['response_time_drivers'] = dict(zip(feature_names, importance_scores))
            
            # Sort by importance
            sorted_features = sorted(feature_analysis['response_time_drivers'].items(), 
                                   key=lambda x: x[1], reverse=True)
            
            # Generate insights for top features
            for feature, importance in sorted_features[:3]:
                if importance > 0.1:  # Only significant features
                    feature_analysis['actionable_insights'].append({
                        'feature': feature,
                        'importance': float(importance),
                        'recommendation': f'Focus on optimizing {feature} as it has {importance:.1%} impact on response time'
                    })
        
        return feature_analysis