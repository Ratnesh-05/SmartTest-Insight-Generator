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
import io
import random

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
        
        # Generate unique filename to avoid conflicts
        import uuid
        original_filename = file.filename
        file_extension = os.path.splitext(original_filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save uploaded file
        file.save(filepath)
        file_size = os.path.getsize(filepath)
        
        # Process the file
        processor = PerformanceDataProcessor()
        df = processor.load_test_data(filepath)
        metrics = processor.calculate_basic_metrics()
        
        # Get data summary
        summary = processor.get_data_summary()
        
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
            elif hasattr(obj, 'dtype'):  # Handle pandas/numpy dtypes
                return str(obj)
            elif hasattr(obj, 'item'):  # Handle numpy scalars
                return obj.item()
            elif isinstance(obj, (int, float, str, bool)):
                return obj
            else:
                return str(obj)
        
        serializable_metrics = convert_to_serializable(metrics)
        
        # Handle summary data more carefully to avoid DateTime64DType issues
        def safe_convert_summary(summary_data):
            if isinstance(summary_data, dict):
                safe_summary = {}
                for key, value in summary_data.items():
                    if key == 'data_types':
                        # Convert pandas dtypes to strings
                        safe_summary[key] = {k: str(v) for k, v in value.items()}
                    else:
                        safe_summary[key] = convert_to_serializable(value)
                return safe_summary
            else:
                return convert_to_serializable(summary_data)
        
        serializable_summary = safe_convert_summary(summary)
        
        # Store file information in database
        from models import UploadedFile, init_database
        import json
        
        SessionLocal = init_database()
        db = SessionLocal()
        
        try:
            # Create database record
            uploaded_file = UploadedFile(
                filename=unique_filename,
                original_filename=original_filename,
                file_path=filepath,
                file_size=file_size,
                file_type=file_extension[1:],  # Remove the dot
                processed=True,
                total_records=len(df),
                metrics_json=json.dumps(serializable_metrics),
                summary_json=json.dumps(serializable_summary)
            )
            
            db.add(uploaded_file)
            db.commit()
            db.refresh(uploaded_file)
            
            file_id = uploaded_file.id
            
        except Exception as e:
            db.rollback()
            # Clean up file if database save fails
            if os.path.exists(filepath):
                os.remove(filepath)
            raise e
        finally:
            db.close()
        
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
            elif hasattr(obj, 'dtype'):  # Handle pandas/numpy dtypes
                return str(obj)
            elif hasattr(obj, 'item'):  # Handle numpy scalars
                return obj.item()
            elif isinstance(obj, (int, float, str, bool)):
                return obj
            else:
                return str(obj)
        
        serializable_metrics = convert_to_serializable(metrics)
        
        # Handle summary data more carefully to avoid DateTime64DType issues
        def safe_convert_summary(summary_data):
            if isinstance(summary_data, dict):
                safe_summary = {}
                for key, value in summary_data.items():
                    if key == 'data_types':
                        # Convert pandas dtypes to strings
                        safe_summary[key] = {k: str(v) for k, v in value.items()}
                    else:
                        safe_summary[key] = convert_to_serializable(value)
                return safe_summary
            else:
                return convert_to_serializable(summary_data)
        
        serializable_summary = safe_convert_summary(summary)
        
        return jsonify({
            'success': True,
            'message': f'Successfully processed {len(df)} records',
            'file_id': file_id,
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
        
        # Determine file extension from the data URL
        data_url = file_data.split(',')[0]
        if 'csv' in data_url:
            file_extension = '.csv'
        elif 'json' in data_url:
            file_extension = '.json'
        elif 'xlsx' in data_url or 'excel' in data_url:
            file_extension = '.xlsx'
        else:
            file_extension = '.xlsx'  # Default to Excel
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
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

@app.route('/api/reports/comparison-by-id', methods=['POST'])
def generate_comparison_report_by_id():
    """Generate comparison report using file IDs from database"""
    try:
        data = request.get_json()
        file_a_id = data.get('file_a_id')
        file_b_id = data.get('file_b_id')
        report_format = data.get('format', 'pdf')
        
        if not file_a_id or not file_b_id:
            return jsonify({'error': 'Both file IDs are required for comparison'}), 400
        
        # Get files from database
        from models import UploadedFile, init_database
        
        SessionLocal = init_database()
        db = SessionLocal()
        
        try:
            file_a = db.query(UploadedFile).filter(
                UploadedFile.id == file_a_id,
                UploadedFile.is_active == True
            ).first()
            
            file_b = db.query(UploadedFile).filter(
                UploadedFile.id == file_b_id,
                UploadedFile.is_active == True
            ).first()
            
            if not file_a or not file_b:
                return jsonify({'error': 'One or both files not found in database'}), 404
            
            # Check if files exist on disk
            if not os.path.exists(file_a.file_path):
                return jsonify({'error': f'File A not found on disk: {file_a.original_filename}'}), 404
                
            if not os.path.exists(file_b.file_path):
                return jsonify({'error': f'File B not found on disk: {file_b.original_filename}'}), 404
            
            # Process both files
            processor = PerformanceDataProcessor()
            
            # Load data from both files
            df_a = processor.load_test_data(file_a.file_path)
            metrics_a = processor.calculate_basic_metrics()
            
            processor_b = PerformanceDataProcessor()
            df_b = processor_b.load_test_data(file_b.file_path)
            metrics_b = processor_b.calculate_basic_metrics()
            
            # Convert metrics to ensure numeric values and flatten structure
            def convert_metrics(metrics):
                """Convert metrics to ensure all values are numeric and flatten structure"""
                converted = {}
                for key, value in metrics.items():
                    if isinstance(value, dict):
                        # Flatten nested metrics
                        for sub_key, sub_value in value.items():
                            flat_key = f"{key}_{sub_key}"
                            try:
                                converted[flat_key] = float(sub_value) if sub_value is not None else 0.0
                            except (ValueError, TypeError):
                                converted[flat_key] = 0.0
                    else:
                        try:
                            converted[key] = float(value) if value is not None else 0.0
                        except (ValueError, TypeError):
                            converted[key] = 0.0
                return converted
            
            metrics_a_converted = convert_metrics(metrics_a)
            metrics_b_converted = convert_metrics(metrics_b)
            
            # Generate comparison analysis
            comparison_data = {
                'test_a': {
                    'name': file_a.original_filename,
                    'metrics': metrics_a_converted,
                    'data_summary': processor.get_data_summary()
                },
                'test_b': {
                    'name': file_b.original_filename,
                    'metrics': metrics_b_converted,
                    'data_summary': processor_b.get_data_summary()
                },
                'comparison': {
                    'response_time_diff': metrics_a_converted.get('response_time_mean', 0) - metrics_b_converted.get('response_time_mean', 0),
                    'error_rate_diff': metrics_a_converted.get('errors_error_rate', 0) - metrics_b_converted.get('errors_error_rate', 0),
                    'throughput_diff': metrics_a_converted.get('throughput_mean', 0) - metrics_b_converted.get('throughput_mean', 0),
                    'improvement_percentage': calculate_improvement_percentage(metrics_a_converted, metrics_b_converted)
                }
            }
            
            if report_format == 'pdf':
                # Generate PDF comparison report
                pdf_content = create_comparison_pdf_report(comparison_data)
                
                response = send_file(
                    io.BytesIO(pdf_content),
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=f'comparison_{file_a.original_filename}_vs_{file_b.original_filename}.pdf'
                )
                return response
                
            else:
                return jsonify({'error': 'Unsupported format'}), 400
                
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/comparison', methods=['POST'])
def generate_comparison_report():
    """Generate comparison report between two test runs"""
    try:
        data = request.get_json()
        file_a_path = data.get('file_a_path')
        file_b_path = data.get('file_b_path')
        report_format = data.get('format', 'pdf')
        
        if not file_a_path or not file_b_path:
            return jsonify({'error': 'Both files are required for comparison'}), 400
        
        # Check if files exist, if not, try to find them in upload folder
        if not os.path.exists(file_a_path):
            file_a_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(file_a_path))
        if not os.path.exists(file_b_path):
            file_b_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(file_b_path))
            
        if not os.path.exists(file_a_path) or not os.path.exists(file_b_path):
            return jsonify({'error': 'One or both files not found. Please upload files first.'}), 404
        
        # Process both files
        processor = PerformanceDataProcessor()
        
        # Load data from both files
        df_a = processor.load_test_data(file_a_path)
        metrics_a = processor.calculate_basic_metrics()
        print(f"DEBUG: Metrics A structure: {metrics_a}")
        
        processor_b = PerformanceDataProcessor()
        df_b = processor_b.load_test_data(file_b_path)
        metrics_b = processor_b.calculate_basic_metrics()
        print(f"DEBUG: Metrics B structure: {metrics_b}")
        
        # Convert metrics to ensure numeric values and flatten structure
        def convert_metrics(metrics):
            """Convert metrics to ensure all values are numeric and flatten structure"""
            converted = {}
            print(f"DEBUG: Converting metrics: {metrics}")
            for key, value in metrics.items():
                print(f"DEBUG: Processing key '{key}' with value '{value}' (type: {type(value)})")
                if isinstance(value, dict):
                    # Flatten nested metrics
                    for sub_key, sub_value in value.items():
                        flat_key = f"{key}_{sub_key}"
                        try:
                            converted[flat_key] = float(sub_value) if sub_value is not None else 0.0
                            print(f"DEBUG: Converted {flat_key} = {converted[flat_key]}")
                        except (ValueError, TypeError) as e:
                            print(f"DEBUG: Error converting {flat_key}: {e}")
                            converted[flat_key] = 0.0
                else:
                    try:
                        converted[key] = float(value) if value is not None else 0.0
                        print(f"DEBUG: Converted {key} = {converted[key]}")
                    except (ValueError, TypeError) as e:
                        print(f"DEBUG: Error converting {key}: {e}")
                        converted[key] = 0.0
            print(f"DEBUG: Final converted metrics: {converted}")
            return converted
        
        metrics_a_converted = convert_metrics(metrics_a)
        metrics_b_converted = convert_metrics(metrics_b)
        
        # Generate comparison analysis
        comparison_data = {
            'test_a': {
                'name': os.path.basename(file_a_path),
                'metrics': metrics_a_converted,
                'data_summary': processor.get_data_summary()
            },
            'test_b': {
                'name': os.path.basename(file_b_path),
                'metrics': metrics_b_converted,
                'data_summary': processor_b.get_data_summary()
            },
            'comparison': {
                'response_time_diff': metrics_a_converted.get('response_time_mean', 0) - metrics_b_converted.get('response_time_mean', 0),
                'error_rate_diff': metrics_a_converted.get('errors_error_rate', 0) - metrics_b_converted.get('errors_error_rate', 0),
                'throughput_diff': metrics_a_converted.get('throughput_mean', 0) - metrics_b_converted.get('throughput_mean', 0),
                'improvement_percentage': calculate_improvement_percentage(metrics_a_converted, metrics_b_converted)
            }
        }
        
        if report_format == 'pdf':
            # Generate PDF comparison report
            pdf_content = create_comparison_pdf_report(comparison_data)
            
            response = send_file(
                io.BytesIO(pdf_content),
                mimetype='application/pdf',
                as_attachment=True,
                download_name='comparison_report.pdf'
            )
            return response
            
        elif report_format == 'excel':
            # Generate Excel comparison report
            excel_generator = ExcelReportGenerator()
            excel_content = excel_generator.generate_comparison_report(comparison_data)
            
            response = send_file(
                io.BytesIO(excel_content),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name='comparison_report.xlsx'
            )
            return response
            
        else:
            return jsonify({'error': 'Unsupported format'}), 400
            
    except Exception as e:
        import traceback
        print(f"ERROR in comparison report: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

def calculate_improvement_percentage(metrics_a, metrics_b):
    """Calculate improvement percentage between two test runs"""
    try:
        # Use flattened metrics structure
        avg_a = float(metrics_a.get('response_time_mean', 0))
        avg_b = float(metrics_b.get('response_time_mean', 0))
        
        if avg_b == 0:
            return 0
        
        improvement = ((avg_b - avg_a) / avg_b) * 100
        return round(improvement, 2)
    except Exception as e:
        print(f"Error calculating improvement: {e}")
        print(f"Metrics A: {metrics_a}")
        print(f"Metrics B: {metrics_b}")
        return 0

def create_comparison_pdf_report(comparison_data):
    """Create a detailed PDF comparison report"""
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    
    # Create PDF buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1f2937')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#374151')
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6
    )
    
    # Build PDF content
    story = []
    
    # Title
    story.append(Paragraph("Performance Test Comparison Report", title_style))
    story.append(Spacer(1, 20))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    story.append(Paragraph(
        f"This report compares two performance test runs: {comparison_data['test_a']['name']} vs {comparison_data['test_b']['name']}. "
        f"The analysis shows key performance differences and recommendations for optimization.",
        normal_style
    ))
    story.append(Spacer(1, 12))
    
    # Comparison Table
    comparison_table_data = [
        ['Metric', 'Test A', 'Test B', 'Difference', 'Improvement'],
        ['Avg Response Time (ms)', 
         f"{comparison_data['test_a']['metrics'].get('avg_response_time', 0):.2f}",
         f"{comparison_data['test_b']['metrics'].get('avg_response_time', 0):.2f}",
         f"{comparison_data['comparison']['response_time_diff']:.2f}",
         f"{comparison_data['comparison']['improvement_percentage']:.1f}%"],
        ['Error Rate (%)',
         f"{comparison_data['test_a']['metrics'].get('error_rate', 0):.2f}",
         f"{comparison_data['test_b']['metrics'].get('error_rate', 0):.2f}",
         f"{comparison_data['comparison']['error_rate_diff']:.2f}",
         "N/A"],
        ['Throughput (req/s)',
         f"{comparison_data['test_a']['metrics'].get('throughput', 0):.2f}",
         f"{comparison_data['test_b']['metrics'].get('throughput', 0):.2f}",
         f"{comparison_data['comparison']['throughput_diff']:.2f}",
         "N/A"]
    ]
    
    comparison_table = Table(comparison_table_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
    comparison_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffffff')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(comparison_table)
    story.append(Spacer(1, 20))
    
    # Detailed Analysis
    story.append(Paragraph("Detailed Analysis", heading_style))
    
    # Test A Details
    story.append(Paragraph(f"Test A: {comparison_data['test_a']['name']}", heading_style))
    test_a_metrics = comparison_data['test_a']['metrics']
    test_a_data = [
        ['Metric', 'Value'],
        ['Average Response Time', f"{test_a_metrics.get('avg_response_time', 0):.2f} ms"],
        ['Maximum Response Time', f"{test_a_metrics.get('max_response_time', 0):.2f} ms"],
        ['Minimum Response Time', f"{test_a_metrics.get('min_response_time', 0):.2f} ms"],
        ['Error Rate', f"{test_a_metrics.get('error_rate', 0):.2f}%"],
        ['Throughput', f"{test_a_metrics.get('throughput', 0):.2f} req/s"],
        ['Total Requests', f"{test_a_metrics.get('total_requests', 0)}"]
    ]
    
    test_a_table = Table(test_a_data, colWidths=[2*inch, 1.5*inch])
    test_a_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dbeafe')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(test_a_table)
    story.append(Spacer(1, 15))
    
    # Test B Details
    story.append(Paragraph(f"Test B: {comparison_data['test_b']['name']}", heading_style))
    test_b_metrics = comparison_data['test_b']['metrics']
    test_b_data = [
        ['Metric', 'Value'],
        ['Average Response Time', f"{test_b_metrics.get('avg_response_time', 0):.2f} ms"],
        ['Maximum Response Time', f"{test_b_metrics.get('max_response_time', 0):.2f} ms"],
        ['Minimum Response Time', f"{test_b_metrics.get('min_response_time', 0):.2f} ms"],
        ['Error Rate', f"{test_b_metrics.get('error_rate', 0):.2f}%"],
        ['Throughput', f"{test_b_metrics.get('throughput', 0):.2f} req/s"],
        ['Total Requests', f"{test_b_metrics.get('total_requests', 0)}"]
    ]
    
    test_b_table = Table(test_b_data, colWidths=[2*inch, 1.5*inch])
    test_b_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fef3c7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#d97706')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fefce8')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#fde68a')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(test_b_table)
    story.append(Spacer(1, 20))
    
    # Recommendations
    story.append(Paragraph("Recommendations", heading_style))
    
    improvement = comparison_data['comparison']['improvement_percentage']
    if improvement > 0:
        recommendation_text = f"Test B shows a {improvement:.1f}% improvement in response time compared to Test A. "
        recommendation_text += "This indicates positive performance optimization."
    elif improvement < 0:
        recommendation_text = f"Test B shows a {abs(improvement):.1f}% degradation in response time compared to Test A. "
        recommendation_text += "Further investigation is recommended to identify performance bottlenecks."
    else:
        recommendation_text = "Both tests show similar performance characteristics. "
        recommendation_text += "Consider running additional tests with different parameters."
    
    story.append(Paragraph(recommendation_text, normal_style))
    story.append(Spacer(1, 12))
    
    # Additional recommendations
    additional_recommendations = [
        "• Monitor system resources during peak load periods",
        "• Implement caching strategies for frequently accessed data",
        "• Optimize database queries and connection pooling",
        "• Consider horizontal scaling for better performance",
        "• Set up automated performance monitoring and alerting"
    ]
    
    for rec in additional_recommendations:
        story.append(Paragraph(rec, normal_style))
    
    story.append(Spacer(1, 20))
    
    # Footer
    story.append(Paragraph(
        f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by Perf Pulse",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, textColor=colors.grey)
    ))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

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

def generate_enhanced_charts(df, metrics, analysis_results):
    """Generate enhanced chart data for advanced visualizations"""
    try:
        charts = {}
        
        # Response Time Distribution (Histogram with gradient)
        if 'response_time' in df.columns:
            rt_data = df['response_time'].dropna()
            charts['response_time_distribution'] = {
                'type': 'histogram',
                'data': {
                    'x': rt_data.tolist(),
                    'nbinsx': 25,
                    'name': 'Response Time Distribution',
                    'marker': {
                        'color': rt_data.tolist(),
                        'colorscale': 'Viridis',
                        'showscale': True
                    }
                },
                'layout': {
                    'title': {'text': 'Response Time Distribution', 'font': {'size': 20, 'color': '#1f2937'}},
                    'xaxis': {'title': 'Response Time (ms)', 'gridcolor': '#e5e7eb'},
                    'yaxis': {'title': 'Frequency', 'gridcolor': '#e5e7eb'},
                    'plot_bgcolor': '#ffffff',
                    'paper_bgcolor': '#ffffff',
                    'bargap': 0.05,
                    'showlegend': False
                }
            }
        
        # Response Time Over Time (Animated Line Chart)
        if 'timestamp' in df.columns and 'response_time' in df.columns:
            df_sorted = df.sort_values('timestamp')
            charts['response_time_trend'] = {
                'type': 'scatter',
                'data': {
                    'x': df_sorted['timestamp'].tolist(),
                    'y': df_sorted['response_time'].tolist(),
                    'mode': 'lines+markers',
                    'name': 'Response Time Trend',
                    'line': {'width': 3, 'color': '#3b82f6'},
                    'marker': {'size': 4, 'color': '#1d4ed8'}
                },
                'layout': {
                    'title': {'text': 'Response Time Over Time', 'font': {'size': 20, 'color': '#1f2937'}},
                    'xaxis': {'title': 'Time', 'gridcolor': '#e5e7eb'},
                    'yaxis': {'title': 'Response Time (ms)', 'gridcolor': '#e5e7eb'},
                    'plot_bgcolor': '#ffffff',
                    'paper_bgcolor': '#ffffff',
                    'hovermode': 'x unified'
                }
            }
        
        # Error Rate Analysis (3D Pie Chart)
        if 'status_code' in df.columns:
            error_counts = df['status_code'].value_counts()
            charts['error_analysis'] = {
                'type': 'pie',
                'data': {
                    'labels': [f'{code} ({count})' for code, count in error_counts.items()],
                    'values': error_counts.values.tolist(),
                    'name': 'Status Code Distribution',
                    'hole': 0.4,
                    'marker': {
                        'colors': ['#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'],
                        'line': {'color': '#ffffff', 'width': 2}
                    }
                },
                'layout': {
                    'title': {'text': 'Status Code Distribution', 'font': {'size': 20, 'color': '#1f2937'}},
                    'height': 500,
                    'showlegend': True,
                    'legend': {'orientation': 'h', 'x': 0.5, 'y': -0.1}
                }
            }
        
        # Performance Metrics Dashboard (Gauge Charts)
        if metrics:
            charts['performance_gauges'] = {
                'type': 'indicator',
                'data': [
                    {
                        'type': 'indicator',
                        'mode': 'gauge+number+delta',
                        'value': metrics.get('avg_response_time', 0),
                        'title': {'text': 'Avg Response Time (ms)', 'font': {'size': 16}},
                        'delta': {'reference': metrics.get('target_response_time', 100)},
                        'gauge': {
                            'axis': {'range': [None, metrics.get('max_response_time', 1000)]},
                            'bar': {'color': '#3b82f6'},
                            'bgcolor': '#f3f4f6',
                            'borderwidth': 2,
                            'bordercolor': '#1f2937',
                            'steps': [
                                {'range': [0, metrics.get('avg_response_time', 0) * 0.5], 'color': '#10b981'},
                                {'range': [metrics.get('avg_response_time', 0) * 0.5, metrics.get('avg_response_time', 0)], 'color': '#f59e0b'},
                                {'range': [metrics.get('avg_response_time', 0), metrics.get('max_response_time', 1000)], 'color': '#ef4444'}
                            ],
                            'threshold': {
                                'line': {'color': '#ef4444', 'width': 4},
                                'thickness': 0.75,
                                'value': metrics.get('max_response_time', 1000) * 0.8
                            }
                        }
                    },
                    {
                        'type': 'indicator',
                        'mode': 'gauge+number+delta',
                        'value': metrics.get('error_rate', 0),
                        'title': {'text': 'Error Rate (%)', 'font': {'size': 16}},
                        'delta': {'reference': 5},
                        'gauge': {
                            'axis': {'range': [None, 100]},
                            'bar': {'color': '#ef4444'},
                            'bgcolor': '#f3f4f6',
                            'borderwidth': 2,
                            'bordercolor': '#1f2937',
                            'steps': [
                                {'range': [0, 5], 'color': '#10b981'},
                                {'range': [5, 10], 'color': '#f59e0b'},
                                {'range': [10, 100], 'color': '#ef4444'}
                            ],
                            'threshold': {
                                'line': {'color': '#ef4444', 'width': 4},
                                'thickness': 0.75,
                                'value': 10
                            }
                        }
                    }
                ]
            }
        
        # Throughput Analysis (3D Bar Chart)
        if 'throughput' in metrics:
            charts['throughput_analysis'] = {
                'type': 'bar',
                'data': {
                    'x': ['Current', 'Target', 'Peak'],
                    'y': [metrics.get('throughput', 0), metrics.get('target_throughput', 0), metrics.get('peak_throughput', 0)],
                    'name': 'Throughput Comparison',
                    'marker': {
                        'color': ['#10b981', '#f59e0b', '#ef4444'],
                        'line': {'color': '#ffffff', 'width': 2}
                    }
                },
                'layout': {
                    'title': {'text': 'Throughput Analysis', 'font': {'size': 20, 'color': '#1f2937'}},
                    'xaxis': {'title': 'Metric Type', 'gridcolor': '#e5e7eb'},
                    'yaxis': {'title': 'Requests/Second', 'gridcolor': '#e5e7eb'},
                    'plot_bgcolor': '#ffffff',
                    'paper_bgcolor': '#ffffff',
                    'bargap': 0.3
                }
            }
        
        # Anomaly Detection (Scatter Plot with Clusters)
        if 'anomalies' in analysis_results:
            anomalies = analysis_results['anomalies']
            if anomalies and len(anomalies) > 0:
                normal_indices = [i for i, is_anomaly in enumerate(anomalies) if not is_anomaly]
                anomaly_indices = [i for i, is_anomaly in enumerate(anomalies) if is_anomaly]
                
                charts['anomaly_detection'] = {
                    'type': 'scatter',
                    'data': [
                        {
                            'x': [df.iloc[i]['response_time'] for i in normal_indices],
                            'y': [i for i in normal_indices],
                            'mode': 'markers',
                            'name': 'Normal Requests',
                            'marker': {
                                'color': '#10b981',
                                'size': 8,
                                'symbol': 'circle',
                                'line': {'color': '#ffffff', 'width': 1}
                            }
                        },
                        {
                            'x': [df.iloc[i]['response_time'] for i in anomaly_indices],
                            'y': [i for i in anomaly_indices],
                            'mode': 'markers',
                            'name': 'Anomalies',
                            'marker': {
                                'color': '#ef4444',
                                'size': 12,
                                'symbol': 'diamond',
                                'line': {'color': '#ffffff', 'width': 2}
                            }
                        }
                    ],
                    'layout': {
                        'title': {'text': 'Anomaly Detection', 'font': {'size': 20, 'color': '#1f2937'}},
                        'xaxis': {'title': 'Response Time (ms)', 'gridcolor': '#e5e7eb'},
                        'yaxis': {'title': 'Request Index', 'gridcolor': '#e5e7eb'},
                        'plot_bgcolor': '#ffffff',
                        'paper_bgcolor': '#ffffff',
                        'showlegend': True
                    }
                }
        
        # Performance Heatmap
        if len(df) > 10:
            # Create time-based heatmap
            df_sample = df.sample(n=min(100, len(df)))
            charts['performance_heatmap'] = {
                'type': 'heatmap',
                'data': {
                    'z': [df_sample['response_time'].tolist()],
                    'x': list(range(len(df_sample))),
                    'y': ['Response Time'],
                    'colorscale': 'Viridis',
                    'showscale': True
                },
                'layout': {
                    'title': {'text': 'Performance Heatmap', 'font': {'size': 20, 'color': '#1f2937'}},
                    'xaxis': {'title': 'Request Index'},
                    'yaxis': {'title': 'Metrics'},
                    'plot_bgcolor': '#ffffff',
                    'paper_bgcolor': '#ffffff'
                }
            }
        
        # Performance Trends (Multi-line Chart with Confidence Intervals)
        if len(df) > 10:
            df_sample = df.sample(n=min(50, len(df))).sort_values('timestamp' if 'timestamp' in df.columns else df.index)
            
            # Calculate moving average and standard deviation
            moving_avg = df_sample['response_time'].rolling(window=5).mean()
            std_dev = df_sample['response_time'].rolling(window=5).std()
            
            charts['performance_trends'] = {
                'type': 'scatter',
                'data': [
                    {
                        'x': df_sample.index.tolist(),
                        'y': df_sample['response_time'].tolist(),
                        'mode': 'lines+markers',
                        'name': 'Response Time',
                        'line': {'color': '#3b82f6', 'width': 2},
                        'marker': {'size': 4}
                    },
                    {
                        'x': df_sample.index.tolist(),
                        'y': moving_avg.tolist(),
                        'mode': 'lines',
                        'name': 'Moving Average',
                        'line': {'color': '#10b981', 'dash': 'dash', 'width': 3}
                    },
                    {
                        'x': df_sample.index.tolist(),
                        'y': (moving_avg + std_dev).tolist(),
                        'mode': 'lines',
                        'name': 'Upper Bound',
                        'line': {'color': '#f59e0b', 'dash': 'dot', 'width': 1},
                        'showlegend': False
                    },
                    {
                        'x': df_sample.index.tolist(),
                        'y': (moving_avg - std_dev).tolist(),
                        'mode': 'lines',
                        'name': 'Lower Bound',
                        'line': {'color': '#f59e0b', 'dash': 'dot', 'width': 1},
                        'fill': 'tonexty',
                        'fillcolor': 'rgba(245, 158, 11, 0.1)',
                        'showlegend': False
                    }
                ],
                'layout': {
                    'title': {'text': 'Performance Trends with Confidence Intervals', 'font': {'size': 20, 'color': '#1f2937'}},
                    'xaxis': {'title': 'Request Index', 'gridcolor': '#e5e7eb'},
                    'yaxis': {'title': 'Response Time (ms)', 'gridcolor': '#e5e7eb'},
                    'plot_bgcolor': '#ffffff',
                    'paper_bgcolor': '#ffffff',
                    'showlegend': True,
                    'hovermode': 'x unified'
                }
            }
        
        # Percentile Analysis (Box Plot)
        if 'response_time' in df.columns:
            charts['percentile_analysis'] = {
                'type': 'box',
                'data': {
                    'y': df['response_time'].dropna().tolist(),
                    'name': 'Response Time Distribution',
                    'boxpoints': 'outliers',
                    'marker': {'color': '#8b5cf6'},
                    'line': {'color': '#1f2937'}
                },
                'layout': {
                    'title': {'text': 'Response Time Percentiles', 'font': {'size': 20, 'color': '#1f2937'}},
                    'yaxis': {'title': 'Response Time (ms)', 'gridcolor': '#e5e7eb'},
                    'plot_bgcolor': '#ffffff',
                    'paper_bgcolor': '#ffffff'
                }
            }
        
        return charts
        
    except Exception as e:
        print(f"Error generating charts: {e}")
        return {}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)