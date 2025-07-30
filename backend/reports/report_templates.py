"""
Report Templates Module
Contains HTML and text templates for generating performance reports
"""

from typing import Dict, Any
from datetime import datetime


class ReportTemplates:
    """HTML and text templates for performance reports"""
    
    @staticmethod
    def get_html_template() -> str:
        """Get HTML template for performance reports"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Performance Test Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .header .subtitle {
            margin-top: 10px;
            opacity: 0.9;
            font-size: 1.1em;
        }
        .content {
            padding: 30px;
        }
        .section {
            margin-bottom: 40px;
            padding: 20px;
            border-radius: 8px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
        }
        .section h2 {
            color: #667eea;
            margin-top: 0;
            font-size: 1.8em;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 10px;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-top: 3px solid #667eea;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        .metric-label {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .table-container {
            overflow-x: auto;
            margin: 20px 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }
        th {
            background: #667eea;
            color: white;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 1px;
        }
        tr:hover {
            background-color: #f8f9fa;
        }
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }
        .alert-warning {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
        }
        .alert-danger {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        .alert-success {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #e9ecef;
        }
        .chart-placeholder {
            width: 100%;
            height: 300px;
            background: #f8f9fa;
            border: 2px dashed #dee2e6;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #6c757d;
            border-radius: 8px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Performance Test Report</h1>
            <div class="subtitle">Generated on {{ report_date }}</div>
        </div>
        
        <div class="content">
            <!-- Executive Summary -->
            <div class="section">
                <h2>📊 Executive Summary</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{{ avg_response_time }}ms</div>
                        <div class="metric-label">Average Response Time</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{{ p95_response_time }}ms</div>
                        <div class="metric-label">95th Percentile</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{{ error_rate }}%</div>
                        <div class="metric-label">Error Rate</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{{ total_requests }}</div>
                        <div class="metric-label">Total Requests</div>
                    </div>
                </div>
            </div>

            <!-- Performance Metrics -->
            <div class="section">
                <h2>⚡ Performance Metrics</h2>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Metric</th>
                                <th>Value</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {{ performance_metrics_rows }}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Error Analysis -->
            <div class="section">
                <h2>🚨 Error Analysis</h2>
                {{ error_alerts }}
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Error Type</th>
                                <th>Count</th>
                                <th>Percentage</th>
                            </tr>
                        </thead>
                        <tbody>
                            {{ error_analysis_rows }}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Trends and Insights -->
            <div class="section">
                <h2>📈 Trends and Insights</h2>
                <div class="chart-placeholder">
                    Response Time Trend Chart (Placeholder)
                </div>
                {{ insights_content }}
            </div>

            <!-- Recommendations -->
            <div class="section">
                <h2>💡 Recommendations</h2>
                {{ recommendations_content }}
            </div>
        </div>
        
        <div class="footer">
            <p>Report generated by Smart Test Insight Generator</p>
            <p>For questions or support, contact your performance testing team</p>
        </div>
    </div>
</body>
</html>
        """
    
    @staticmethod
    def get_executive_summary_template() -> str:
        """Get executive summary template"""
        return """
# Performance Test Executive Summary

**Report Date:** {{ report_date }}
**Test Duration:** {{ test_duration }}

## Key Performance Indicators

- **Average Response Time:** {{ avg_response_time }}ms
- **95th Percentile Response Time:** {{ p95_response_time }}ms
- **99th Percentile Response Time:** {{ p99_response_time }}ms
- **Error Rate:** {{ error_rate }}%
- **Total Requests Processed:** {{ total_requests }}
- **Peak Throughput:** {{ peak_throughput }} req/sec

## Performance Status: {{ overall_status }}

{{ status_summary }}

## Critical Issues
{{ critical_issues }}

## Key Recommendations
{{ key_recommendations }}

---
*Generated by Smart Test Insight Generator*
        """
    
    @staticmethod
    def get_detailed_report_template() -> str:
        """Get detailed performance report template"""
        return """
# Detailed Performance Analysis Report

Generated: {{ report_date }}

## Test Configuration
- **Test Name:** {{ test_name }}
- **Environment:** {{ environment }}
- **Load Pattern:** {{ load_pattern }}
- **Duration:** {{ test_duration }}
- **Max Concurrent Users:** {{ max_users }}

## Response Time Analysis

### Statistical Summary
| Metric | Value (ms) |
|--------|------------|
| Minimum | {{ min_response_time }} |
| Maximum | {{ max_response_time }} |
| Average | {{ avg_response_time }} |
| Median | {{ median_response_time }} |
| Standard Deviation | {{ std_response_time }} |
| 50th Percentile | {{ p50_response_time }} |
| 90th Percentile | {{ p90_response_time }} |
| 95th Percentile | {{ p95_response_time }} |
| 99th Percentile | {{ p99_response_time }} |

### Response Time Distribution
{{ response_time_distribution }}

## Throughput Analysis
{{ throughput_analysis }}

## Error Analysis
{{ error_analysis }}

## Resource Utilization
{{ resource_utilization }}

## Performance Trends
{{ performance_trends }}

## Anomaly Detection Results
{{ anomaly_results }}

## Detailed Recommendations
{{ detailed_recommendations }}

## Appendix
### Test Data Summary
{{ test_data_summary }}

### Log Analysis
{{ log_analysis_summary }}

---
*Detailed analysis generated by Smart Test Insight Generator*
        """
    
    @staticmethod
    def format_metric_row(metric: str, value: Any, status: str = "OK") -> str:
        """Format a metric row for HTML table"""
        status_class = {
            "OK": "alert-success",
            "WARNING": "alert-warning", 
            "CRITICAL": "alert-danger"
        }.get(status, "")
        
        return f"""
            <tr>
                <td>{metric}</td>
                <td>{value}</td>
                <td><span class="alert {status_class}">{status}</span></td>
            </tr>
        """
    
    @staticmethod
    def format_error_alert(message: str, alert_type: str = "warning") -> str:
        """Format error alert for HTML"""
        return f'<div class="alert alert-{alert_type}">{message}</div>'
    
    @staticmethod
    def format_recommendations_list(recommendations: list) -> str:
        """Format recommendations as HTML list"""
        if not recommendations:
            return "<p>No specific recommendations at this time.</p>"
        
        html = "<ul>"
        for rec in recommendations:
            html += f"<li>{rec}</li>"
        html += "</ul>"
        return html
    
    @staticmethod
    def format_insights_content(insights: Dict) -> str:
        """Format insights content for HTML"""
        content = ""
        
        if 'key_findings' in insights and insights['key_findings']:
            content += "<h3>🔍 Key Findings</h3><ul>"
            for finding in insights['key_findings']:
                content += f"<li>{finding}</li>"
            content += "</ul>"
        
        if 'risk_areas' in insights and insights['risk_areas']:
            content += "<h3>⚠️ Risk Areas</h3><ul>"
            for risk in insights['risk_areas']:
                content += f"<li>{risk}</li>"
            content += "</ul>"
        
        return content if content else "<p>No specific insights available.</p>"


class EmailTemplates:
    """Email templates for automated reporting"""
    
    @staticmethod
    def get_alert_template() -> str:
        """Get email alert template"""
        return """
Subject: 🚨 Performance Test Alert - {{ alert_type }}

Dear Team,

A performance test alert has been triggered:

**Alert Type:** {{ alert_type }}
**Severity:** {{ severity }}
**Time:** {{ timestamp }}

**Details:**
{{ alert_details }}

**Key Metrics:**
- Response Time: {{ response_time }}ms
- Error Rate: {{ error_rate }}%
- Throughput: {{ throughput }} req/sec

**Recommended Actions:**
{{ recommended_actions }}

Please investigate immediately if this is a critical alert.

Best regards,
Smart Test Insight Generator
        """
    
    @staticmethod
    def get_daily_summary_template() -> str:
        """Get daily summary email template"""
        return """
Subject: 📊 Daily Performance Summary - {{ date }}

Hello Team,

Here's your daily performance testing summary:

**Overall Status:** {{ overall_status }}

**Today's Highlights:**
{{ daily_highlights }}

**Performance Trends:**
{{ performance_trends }}

**Action Items:**
{{ action_items }}

View the full report: {{ report_link }}

Best regards,
Smart Test Insight Generator
        """ 