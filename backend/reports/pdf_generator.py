"""
PDF Report Generator Module
Handles PDF report generation using PDFkit
"""

import pdfkit
from jinja2 import Template
from typing import Dict, List, Optional
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PDFReportGenerator:
    """Generates PDF reports for performance test analysis"""
    
    def __init__(self, wkhtmltopdf_path: Optional[str] = None):
        """
        Initialize PDF generator
        
        Args:
            wkhtmltopdf_path: Path to wkhtmltopdf executable
        """
        self.wkhtmltopdf_path = wkhtmltopdf_path
        self.config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path) if wkhtmltopdf_path else None
        
    def generate_performance_report(self, data: Dict, output_path: str) -> str:
        """
        Generate comprehensive performance test report
        
        Args:
            data: Performance test data and metrics
            output_path: Path to save the PDF file
            
        Returns:
            str: Path to generated PDF file
        """
        try:
            html_content = self._create_performance_html(data)
            pdfkit.from_string(html_content, output_path, configuration=self.config)
            logger.info(f"Performance report generated: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error generating performance report: {str(e)}")
            raise
    
    def generate_executive_summary(self, data: Dict, output_path: str) -> str:
        """
        Generate executive summary report
        
        Args:
            data: Summary data
            output_path: Path to save the PDF file
            
        Returns:
            str: Path to generated PDF file
        """
        try:
            html_content = self._create_executive_html(data)
            pdfkit.from_string(html_content, output_path, configuration=self.config)
            logger.info(f"Executive summary generated: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error generating executive summary: {str(e)}")
            raise
    
    def generate_log_analysis_report(self, log_data: Dict, output_path: str) -> str:
        """
        Generate log analysis report
        
        Args:
            log_data: Log analysis data
            output_path: Path to save the PDF file
            
        Returns:
            str: Path to generated PDF file
        """
        try:
            html_content = self._create_log_analysis_html(log_data)
            pdfkit.from_string(html_content, output_path, configuration=self.config)
            logger.info(f"Log analysis report generated: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error generating log analysis report: {str(e)}")
            raise
    
    def _create_performance_html(self, data: Dict) -> str:
        """Create HTML content for performance report"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Performance Test Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #2c3e50; color: white; padding: 20px; text-align: center; }
                .section { margin: 20px 0; }
                .metric { background-color: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .metric-title { font-weight: bold; color: #2c3e50; }
                .metric-value { font-size: 18px; color: #27ae60; }
                .error { color: #e74c3c; }
                .warning { color: #f39c12; }
                .success { color: #27ae60; }
                table { width: 100%; border-collapse: collapse; margin: 10px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .chart-container { margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Performance Test Report</h1>
                <p>Generated on {{ generation_time }}</p>
            </div>
            
            <div class="section">
                <h2>Test Overview</h2>
                <div class="metric">
                    <div class="metric-title">Test Duration</div>
                    <div class="metric-value">{{ test_duration }}</div>
                </div>
                <div class="metric">
                    <div class="metric-title">Total Requests</div>
                    <div class="metric-value">{{ total_requests }}</div>
                </div>
                <div class="metric">
                    <div class="metric-title">Error Rate</div>
                    <div class="metric-value {{ error_rate_class }}">{{ error_rate }}%</div>
                </div>
            </div>
            
            <div class="section">
                <h2>Response Time Analysis</h2>
                <table>
                    <tr>
                        <th>Metric</th>
                        <th>Value (ms)</th>
                    </tr>
                    <tr><td>Minimum</td><td>{{ response_time.min }}</td></tr>
                    <tr><td>Maximum</td><td>{{ response_time.max }}</td></tr>
                    <tr><td>Average</td><td>{{ response_time.mean }}</td></tr>
                    <tr><td>Median</td><td>{{ response_time.median }}</td></tr>
                    <tr><td>90th Percentile</td><td>{{ response_time.p90 }}</td></tr>
                    <tr><td>95th Percentile</td><td>{{ response_time.p95 }}</td></tr>
                    <tr><td>99th Percentile</td><td>{{ response_time.p99 }}</td></tr>
                </table>
            </div>
            
            <div class="section">
                <h2>Throughput Analysis</h2>
                <table>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                    <tr><td>Average RPS</td><td>{{ throughput.mean }}</td></tr>
                    <tr><td>Peak RPS</td><td>{{ throughput.max }}</td></tr>
                    <tr><td>Total Requests</td><td>{{ throughput.total_requests }}</td></tr>
                </table>
            </div>
            
            {% if anomalies %}
            <div class="section">
                <h2>Anomalies Detected</h2>
                <table>
                    <tr>
                        <th>Timestamp</th>
                        <th>Value</th>
                        <th>Z-Score</th>
                    </tr>
                    {% for anomaly in anomalies %}
                    <tr>
                        <td>{{ anomaly.timestamp }}</td>
                        <td>{{ anomaly.value }}</td>
                        <td>{{ anomaly.z_score }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            {% endif %}
            
            <div class="section">
                <h2>Recommendations</h2>
                <ul>
                    {% for recommendation in recommendations %}
                    <li>{{ recommendation }}</li>
                    {% endfor %}
                </ul>
            </div>
        </body>
        </html>
        """
        
        # Prepare template data
        template_data = {
            'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'test_duration': data.get('test_duration', 'N/A'),
            'total_requests': data.get('total_requests', 0),
            'error_rate': data.get('error_rate', 0),
            'error_rate_class': 'error' if data.get('error_rate', 0) > 5 else 'success',
            'response_time': data.get('response_time', {}),
            'throughput': data.get('throughput', {}),
            'anomalies': data.get('anomalies', []),
            'recommendations': data.get('recommendations', [])
        }
        
        return Template(template).render(**template_data)
    
    def _create_executive_html(self, data: Dict) -> str:
        """Create HTML content for executive summary"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Executive Summary</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #2c3e50; color: white; padding: 20px; text-align: center; }
                .summary-box { background-color: #ecf0f1; padding: 20px; margin: 20px 0; border-radius: 5px; }
                .key-metric { font-size: 24px; font-weight: bold; color: #2c3e50; }
                .status { padding: 5px 10px; border-radius: 3px; color: white; }
                .status.pass { background-color: #27ae60; }
                .status.fail { background-color: #e74c3c; }
                .status.warning { background-color: #f39c12; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Executive Summary</h1>
                <p>Performance Test Results</p>
            </div>
            
            <div class="summary-box">
                <h2>Overall Status</h2>
                <div class="status {{ overall_status }}">{{ overall_status.upper() }}</div>
            </div>
            
            <div class="summary-box">
                <h2>Key Metrics</h2>
                <div class="key-metric">Average Response Time: {{ avg_response_time }}ms</div>
                <div class="key-metric">Throughput: {{ throughput }} RPS</div>
                <div class="key-metric">Error Rate: {{ error_rate }}%</div>
            </div>
            
            <div class="summary-box">
                <h2>Key Findings</h2>
                <ul>
                    {% for finding in key_findings %}
                    <li>{{ finding }}</li>
                    {% endfor %}
                </ul>
            </div>
            
            <div class="summary-box">
                <h2>Recommendations</h2>
                <ul>
                    {% for recommendation in recommendations %}
                    <li>{{ recommendation }}</li>
                    {% endfor %}
                </ul>
            </div>
        </body>
        </html>
        """
        
        template_data = {
            'overall_status': data.get('overall_status', 'pass'),
            'avg_response_time': data.get('avg_response_time', 0),
            'throughput': data.get('throughput', 0),
            'error_rate': data.get('error_rate', 0),
            'key_findings': data.get('key_findings', []),
            'recommendations': data.get('recommendations', [])
        }
        
        return Template(template).render(**template_data)
    
    def _create_log_analysis_html(self, log_data: Dict) -> str:
        """Create HTML content for log analysis report"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Log Analysis Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #2c3e50; color: white; padding: 20px; text-align: center; }
                .section { margin: 20px 0; }
                .metric { background-color: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }
                table { width: 100%; border-collapse: collapse; margin: 10px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Log Analysis Report</h1>
                <p>Generated on {{ generation_time }}</p>
            </div>
            
            <div class="section">
                <h2>Log Summary</h2>
                <div class="metric">
                    <strong>Total Entries:</strong> {{ total_entries }}
                </div>
                <div class="metric">
                    <strong>Error Rate:</strong> {{ error_rate }}%
                </div>
                <div class="metric">
                    <strong>Time Range:</strong> {{ time_range }}
                </div>
            </div>
            
            <div class="section">
                <h2>Error Analysis</h2>
                <table>
                    <tr>
                        <th>Error Message</th>
                        <th>Count</th>
                    </tr>
                    {% for error in top_errors %}
                    <tr>
                        <td>{{ error.message }}</td>
                        <td>{{ error.count }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            
            <div class="section">
                <h2>Performance Analysis</h2>
                <table>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                    <tr><td>Average Response Time</td><td>{{ avg_response_time }}ms</td></tr>
                    <tr><td>Max Response Time</td><td>{{ max_response_time }}ms</td></tr>
                    <tr><td>Min Response Time</td><td>{{ min_response_time }}ms</td></tr>
                </table>
            </div>
            
            {% if anomalies %}
            <div class="section">
                <h2>Detected Anomalies</h2>
                <table>
                    <tr>
                        <th>Timestamp</th>
                        <th>Value</th>
                        <th>Z-Score</th>
                    </tr>
                    {% for anomaly in anomalies %}
                    <tr>
                        <td>{{ anomaly.timestamp }}</td>
                        <td>{{ anomaly.value }}</td>
                        <td>{{ anomaly.z_score }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            {% endif %}
        </body>
        </html>
        """
        
        template_data = {
            'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_entries': log_data.get('total_entries', 0),
            'error_rate': log_data.get('error_rate', 0),
            'time_range': log_data.get('time_range', 'N/A'),
            'top_errors': log_data.get('top_errors', []),
            'avg_response_time': log_data.get('avg_response_time', 0),
            'max_response_time': log_data.get('max_response_time', 0),
            'min_response_time': log_data.get('min_response_time', 0),
            'anomalies': log_data.get('anomalies', [])
        }
        
        return Template(template).render(**template_data)