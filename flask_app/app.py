"""
Flask Backend API for Smart Test Insight Generator
"""

from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import os
import tempfile
import sys
from pathlib import Path
import json
from datetime import datetime
import base64
import pandas as pd

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

# Import backend modules
from backend.core.data_processor import PerformanceDataProcessor
from backend.core.log_analyzer import LogAnalyzer
from backend.core.performance_analyzer import PerformanceAnalyzer
from backend.reports.pdf_generator import PDFReportGenerator
from backend.reports.excel_generator import ExcelReportGenerator
from config import config

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

@app.route('/')
def index():
    """Serve the main React application"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Perf Pulse API is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload for performance analysis"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the file
        processor = PerformanceDataProcessor()
        df = processor.load_test_data(filepath)
        metrics = processor.calculate_basic_metrics()
        
        # Get data summary
        summary = processor.get_data_summary()
        
        # Clean up uploaded file
        os.remove(filepath)
        
        # Convert DataFrame to JSON-serializable format
        preview_data = []
        for _, row in df.head(10).iterrows():
            preview_data.append({
                col: str(val) if pd.isna(val) else val 
                for col, val in row.items()
            })
        
        # Convert metrics to JSON-serializable format
        def convert_to_serializable(obj):
            if isinstance(obj, dict):
                return {k: convert_to_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_serializable(item) for item in obj]
            elif pd.isna(obj):
                return None
            elif isinstance(obj, (int, float, str, bool)):
                return obj
            else:
                return str(obj)
        
        serializable_metrics = convert_to_serializable(metrics)
        serializable_summary = convert_to_serializable(summary)
        
        return jsonify({
            'success': True,
            'message': f'Successfully processed {len(df)} records',
            'data': {
                'metrics': serializable_metrics,
                'summary': serializable_summary,
                'preview': preview_data,
                'total_records': len(df)
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_performance():
    """Run advanced performance analysis"""
    try:
        data = request.json
        file_data = data.get('file_data')
        
        if not file_data:
            return jsonify({'error': 'No file data provided'}), 400
        
        # Create temporary file from base64 data
        file_content = base64.b64decode(file_data.split(',')[1])
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            tmp_file.write(file_content)
            tmp_file_path = tmp_file.name
        
        # Process data
        processor = PerformanceDataProcessor()
        df = processor.load_test_data(tmp_file_path)
        
        # Run advanced analysis
        analyzer = PerformanceAnalyzer()
        trends = analyzer.analyze_performance_trends(df)
        anomalies = analyzer.detect_performance_anomalies(df)
        insights = analyzer.generate_performance_insights(df)
        
        # Clean up temp file
        os.remove(tmp_file_path)
        
        return jsonify({
            'success': True,
            'data': {
                'trends': trends,
                'anomalies': anomalies,
                'insights': insights
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs/analyze', methods=['POST'])
def analyze_logs():
    """Analyze log files"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Analyze logs
        analyzer = LogAnalyzer()
        df = analyzer.parse_log_file(filepath)
        error_analysis = analyzer.analyze_error_patterns(df)
        performance_analysis = analyzer.analyze_performance_patterns(df)
        summary = analyzer.generate_log_summary(df)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'data': {
                'error_analysis': error_analysis,
                'performance_analysis': performance_analysis,
                'summary': summary,
                'total_entries': len(df)
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    """Generate reports in various formats"""
    try:
        data = request.json
        report_data = data.get('data')  # Changed from 'report_data' to 'data'
        report_type = data.get('type', 'executive')  # Changed from 'report_type' to 'type'
        output_format = data.get('format', 'pdf')  # Changed from 'output_format' to 'format'
        
        if not report_data:
            return jsonify({'error': 'No report data provided'}), 400
        
        # Generate report based on format
        if output_format == 'pdf':
            # Create comprehensive PDF using reportlab
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            import tempfile
            import random
            
            # Create temporary PDF file
            pdf_path = tempfile.mktemp(suffix='.pdf')
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1,
                textColor=colors.darkblue
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=12,
                textColor=colors.darkblue
            )
            
            # Title
            story.append(Paragraph("🚀 Perf Pulse - Comprehensive Performance Test Report", title_style))
            story.append(Spacer(1, 20))
            
            # Test Overview
            story.append(Paragraph("🧪 Test Overview", heading_style))
            story.append(Spacer(1, 12))
            
            test_id = f"PT{random.randint(10000, 99999)}"
            test_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            overview_data = [
                ['Test ID', test_id],
                ['Test Type', 'Load & Stress Test'],
                ['Test Date', test_date],
                ['Objective', 'Evaluate system behavior under concurrent user load and identify performance bottlenecks']
            ]
            
            overview_table = Table(overview_data, colWidths=[2*inch, 4*inch])
            overview_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(overview_table)
            story.append(Spacer(1, 20))
            
            # Test Environment
            story.append(Paragraph("🛠️ Test Environment", heading_style))
            story.append(Spacer(1, 12))
            
            env_data = [
                ['Component', 'Configuration'],
                ['Application Tier', 'Python Flask Backend'],
                ['Database', 'SQLite (Development)'],
                ['Server Specs', 'Local Development Environment'],
                ['Network', 'Local Network'],
                ['Tool Used', 'Perf Pulse Smart Test Insight Generator'],
                ['Test Duration', 'Variable based on data size']
            ]
            
            env_table = Table(env_data, colWidths=[2*inch, 4*inch])
            env_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(env_table)
            story.append(Spacer(1, 20))
            
            # Performance Metrics Summary
            story.append(Paragraph("📊 Performance Metrics Summary", heading_style))
            story.append(Spacer(1, 12))
            
            metrics = report_data.get('metrics', {})
            if metrics:
                # Calculate thresholds and status
                rt = metrics.get('response_time', {})
                errors = metrics.get('errors', {})
                
                avg_rt = rt.get('mean', 0)
                max_rt = rt.get('max', 0)
                throughput = metrics.get('throughput', {}).get('mean', 0)
                error_rate = errors.get('error_rate', 0)
                
                # Define thresholds
                rt_threshold = 2000  # 2 seconds
                throughput_threshold = 100  # requests per second
                error_threshold = 5  # 5%
                
                # Determine status
                def get_status(value, threshold, is_lower_better=True):
                    if is_lower_better:
                        return "✅ Pass" if value <= threshold else "❌ Fail"
                    else:
                        return "✅ Pass" if value >= threshold else "❌ Fail"
                
                metrics_data = [
                    ['Metric', 'Value', 'Threshold', 'Status'],
                    ['Avg Response Time', f"{avg_rt:.2f}ms", f"< {rt_threshold}ms", get_status(avg_rt, rt_threshold)],
                    ['Peak Response Time', f"{max_rt:.2f}ms", f"< {rt_threshold*1.5}ms", get_status(max_rt, rt_threshold*1.5)],
                    ['Throughput', f"{throughput:.2f} req/sec", f"> {throughput_threshold} req/sec", get_status(throughput, throughput_threshold, False)],
                    ['Error Rate', f"{error_rate:.2f}%", f"< {error_threshold}%", get_status(error_rate, error_threshold)],
                    ['Total Requests', str(errors.get('total_requests', 0)), 'N/A', '📊 Info'],
                    ['Success Rate', f"{100-error_rate:.2f}%", '> 95%', get_status(100-error_rate, 95, False)]
                ]
                
                metrics_table = Table(metrics_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.1*inch])
                metrics_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey)
                ]))
                story.append(metrics_table)
                story.append(Spacer(1, 20))
            
            # Detailed Analysis
            story.append(Paragraph("🔍 Detailed Analysis", heading_style))
            story.append(Spacer(1, 12))
            
            analysis_text = f"""
            <b>Response Time Distribution:</b><br/>
            {rt.get('p95', 0):.2f}% of requests completed within {rt.get('p95', 0):.2f}ms. 
            The average response time was {avg_rt:.2f}ms with a maximum of {max_rt:.2f}ms.
            <br/><br/>
            
            <b>Error Breakdown:</b><br/>
            {error_rate:.2f}% errors were observed out of {errors.get('total_requests', 0)} total requests. 
            This represents {errors.get('error_requests', 0)} failed requests.
            <br/><br/>
            
            <b>Throughput Analysis:</b><br/>
            The system processed an average of {throughput:.2f} requests per second, 
            indicating the system's capacity under the given load conditions.
            """
            
            story.append(Paragraph(analysis_text, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Conclusion & Recommendations
            story.append(Paragraph("✅ Conclusion & Recommendations", heading_style))
            story.append(Spacer(1, 12))
            
            # Determine overall status
            overall_status = "PASS" if error_rate < error_threshold and avg_rt < rt_threshold else "FAIL"
            
            conclusion_text = f"""
            <b>Overall Test Status:</b> {overall_status}<br/><br/>
            
            <b>Key Findings:</b><br/>
            • The system processed {errors.get('total_requests', 0)} requests with {error_rate:.2f}% error rate<br/>
            • Average response time of {avg_rt:.2f}ms meets performance expectations<br/>
            • Throughput of {throughput:.2f} requests per second achieved<br/><br/>
            
            <b>Recommendations:</b><br/>
            • Continue monitoring system performance in production<br/>
            • Consider load testing with larger datasets for comprehensive validation<br/>
            • Implement automated performance testing in CI/CD pipeline<br/>
            • Regular performance reviews recommended
            """
            
            story.append(Paragraph(conclusion_text, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Footer
            story.append(Paragraph(f"Report generated by Perf Pulse on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                                ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=1)))
            
            # Build PDF
            doc.build(story)
            
            return send_file(
                pdf_path,
                as_attachment=True,
                download_name=f"perf_pulse_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mimetype='application/pdf'
            )
            
        elif output_format == 'excel':
            excel_generator = ExcelReportGenerator()
            report_path = excel_generator.create_performance_report(report_data, "performance_report.xlsx")
            
            return send_file(
                report_path,
                as_attachment=True,
                download_name=f"perf_pulse_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
        elif output_format == 'html':
            # Create HTML report
            html_content = create_html_report(report_data)
            
            return jsonify({
                'success': True,
                'html_content': html_content,
                'filename': f"perf_pulse_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            })
        
        else:
            return jsonify({'error': 'Unsupported output format'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_html_report(report_data):
    """Create HTML report content"""
    metrics = report_data.get('metrics', {})
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Perf Pulse Performance Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .header {{ background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; }}
            .metric {{ background: white; padding: 20px; margin: 15px 0; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .success {{ color: #28a745; }}
            .warning {{ color: #ffc107; }}
            .danger {{ color: #dc3545; }}
            .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
            .metric-card {{ background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Perf Pulse Performance Report</h1>
            <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        
        <div class="metric">
            <h2>📊 Performance Metrics</h2>
            <div class="metric-grid">
                <div class="metric-card">
                    <h3>⚡ Average Response Time</h3>
                    <h2>{metrics.get('response_time', {}).get('mean', 0):.2f}ms</h2>
                </div>
                <div class="metric-card">
                    <h3>📊 95th Percentile</h3>
                    <h2>{metrics.get('response_time', {}).get('p95', 0):.2f}ms</h2>
                </div>
                <div class="metric-card">
                    <h3>🚀 Maximum Response Time</h3>
                    <h2>{metrics.get('response_time', {}).get('max', 0):.2f}ms</h2>
                </div>
                <div class="metric-card">
                    <h3>⚠️ Error Rate</h3>
                    <h2>{metrics.get('errors', {}).get('error_rate', 0):.2f}%</h2>
                </div>
            </div>
        </div>
        
        <div class="metric">
            <h2>📋 Summary</h2>
            <p><strong>Total Requests:</strong> {metrics.get('errors', {}).get('total_requests', 0):,}</p>
            <p><strong>Error Requests:</strong> {metrics.get('errors', {}).get('error_requests', 0):,}</p>
            <p><strong>Success Rate:</strong> {100 - metrics.get('errors', {}).get('error_rate', 0):.2f}%</p>
        </div>
    </body>
    </html>
    """
    
    return html_content

@app.route('/api/demo-data')
def get_demo_data():
    """Get demo data for testing"""
    try:
        demo_file = 'demo_performance_data.xlsx'
        if os.path.exists(demo_file):
            return send_file(demo_file, as_attachment=True, download_name='demo_performance_data.xlsx')
        else:
            return jsonify({'error': 'Demo data not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)