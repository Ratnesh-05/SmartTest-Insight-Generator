"""
Main Application Entry Point
Smart Test Insight Generator - Performance Testing Analysis Tool
"""

import sys
import logging
from pathlib import Path
from typing import Optional
import argparse

# Add backend to path
sys.path.append(str(Path(__file__).parent / 'backend'))

from config import get_config, config
from backend.core.data_processor import PerformanceDataProcessor
from backend.core.log_analyzer import LogAnalyzer
from backend.core.performance_analyzer import PerformanceAnalyzer
from backend.reports.pdf_generator import PDFReportGenerator
from backend.reports.excel_generator import ExcelReportGenerator
from backend.database.database import init_database, DatabaseService

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, config.LOGGING['level']),
        format=config.LOGGING['format'],
        handlers=[
            logging.FileHandler(config.LOGGING['file']),
            logging.StreamHandler(sys.stdout)
        ]
    )

def initialize_application():
    """Initialize the application"""
    try:
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("Initializing Smart Test Insight Generator...")
        
        # Initialize database
        db_service = init_database(config.get_database_url())
        logger.info("Database initialized successfully")
        
        # Create data directories
        for dir_path in [config.DATA_DIR, config.LOGS_DIR, config.REPORTS_DIR, config.TEST_DATA_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
        logger.info("Data directories created/verified")
        
        return db_service
        
    except Exception as e:
        logging.error(f"Failed to initialize application: {str(e)}")
        raise

def analyze_performance_data(file_path: str, output_format: str = 'pdf') -> dict:
    """
    Analyze performance test data
    
    Args:
        file_path: Path to performance test data file
        output_format: Output format (pdf, excel, html)
        
    Returns:
        dict: Analysis results
    """
    try:
        logger = logging.getLogger(__name__)
        logger.info(f"Starting performance analysis for: {file_path}")
        
        # Initialize components
        data_processor = PerformanceDataProcessor()
        performance_analyzer = PerformanceAnalyzer()
        
        # Load and process data
        df = data_processor.load_test_data(file_path)
        logger.info(f"Loaded {len(df)} records from {file_path}")
        
        # Calculate basic metrics
        basic_metrics = data_processor.calculate_basic_metrics()
        logger.info("Basic metrics calculated")
        
        # Advanced analysis
        trends = performance_analyzer.analyze_performance_trends(df)
        anomalies = performance_analyzer.detect_performance_anomalies(df)
        insights = performance_analyzer.generate_performance_insights(df)
        
        # Prepare results
        results = {
            'data_summary': data_processor.get_data_summary(),
            'metrics': basic_metrics,
            'trends': trends,
            'anomalies': anomalies,
            'insights': insights,
            'raw_data': df
        }
        
        logger.info("Performance analysis completed successfully")
        return results
        
    except Exception as e:
        logging.error(f"Error in performance analysis: {str(e)}")
        raise

def analyze_logs(log_file_path: str) -> dict:
    """
    Analyze log files
    
    Args:
        log_file_path: Path to log file
        
    Returns:
        dict: Log analysis results
    """
    try:
        logger = logging.getLogger(__name__)
        logger.info(f"Starting log analysis for: {log_file_path}")
        
        # Initialize log analyzer
        log_analyzer = LogAnalyzer()
        
        # Parse logs
        df = log_analyzer.parse_log_file(log_file_path)
        logger.info(f"Parsed {len(df)} log entries")
        
        # Analyze logs
        error_analysis = log_analyzer.analyze_error_patterns(df)
        performance_analysis = log_analyzer.analyze_performance_patterns(df)
        anomalies = log_analyzer.detect_anomalies(df)
        summary = log_analyzer.generate_log_summary(df)
        
        results = {
            'summary': summary,
            'error_analysis': error_analysis,
            'performance_analysis': performance_analysis,
            'anomalies': anomalies,
            'parsed_logs': df
        }
        
        logger.info("Log analysis completed successfully")
        return results
        
    except Exception as e:
        logging.error(f"Error in log analysis: {str(e)}")
        raise

def generate_report(analysis_results: dict, report_type: str = 'executive', 
                   output_format: str = 'pdf', output_path: Optional[str] = None) -> str:
    """
    Generate performance report
    
    Args:
        analysis_results: Results from analysis
        report_type: Type of report (executive, detailed, trends)
        output_format: Output format (pdf, excel, html)
        output_path: Output file path
        
    Returns:
        str: Path to generated report
    """
    try:
        logger = logging.getLogger(__name__)
        logger.info(f"Generating {report_type} report in {output_format} format")
        
        if output_format.lower() == 'pdf':
            generator = PDFReportGenerator()
            if not output_path:
                output_path = config.get_report_path(f"performance_report_{report_type}.pdf")
            report_path = generator.generate_performance_report(analysis_results, output_path)
            
        elif output_format.lower() == 'excel':
            generator = ExcelReportGenerator()
            if not output_path:
                output_path = config.get_report_path(f"performance_report_{report_type}.xlsx")
            report_path = generator.create_performance_report(analysis_results, output_path)
            
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
        
        logger.info(f"Report generated successfully: {report_path}")
        return report_path
        
    except Exception as e:
        logging.error(f"Error generating report: {str(e)}")
        raise

def run_streamlit_app():
    """Run Streamlit web application"""
    import subprocess
    import sys
    
    try:
        # Start Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "frontend/streamlit_app.py", "--server.port", "8501"
        ])
    except Exception as e:
        logging.error(f"Error running Streamlit app: {str(e)}")
        raise

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description='Smart Test Insight Generator')
    parser.add_argument('--mode', choices=['cli', 'web'], default='cli',
                       help='Application mode (cli or web)')
    parser.add_argument('--data-file', type=str, help='Performance data file path')
    parser.add_argument('--log-file', type=str, help='Log file path')
    parser.add_argument('--output-format', choices=['pdf', 'excel', 'html'], 
                       default='pdf', help='Report output format')
    parser.add_argument('--report-type', choices=['executive', 'detailed', 'trends'],
                       default='executive', help='Report type')
    parser.add_argument('--output-path', type=str, help='Output file path')
    
    args = parser.parse_args()
    
    try:
        # Initialize application
        db_service = initialize_application()
        
        if args.mode == 'web':
            # Run web application
            print("Starting Smart Test Insight Generator Web Application...")
            print("Access the application at: http://localhost:8501")
            run_streamlit_app()
            
        else:
            # CLI mode
            if not args.data_file and not args.log_file:
                print("Error: Please provide either --data-file or --log-file")
                sys.exit(1)
            
            results = {}
            
            # Analyze performance data
            if args.data_file:
                print(f"Analyzing performance data: {args.data_file}")
                results['performance'] = analyze_performance_data(args.data_file)
            
            # Analyze logs
            if args.log_file:
                print(f"Analyzing log file: {args.log_file}")
                results['logs'] = analyze_logs(args.log_file)
            
            # Generate report
            if results:
                print(f"Generating {args.report_type} report in {args.output_format} format...")
                report_path = generate_report(
                    results, 
                    args.report_type, 
                    args.output_format, 
                    args.output_path
                )
                print(f"Report generated successfully: {report_path}")
            else:
                print("No analysis results to report")
                
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Application error: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)
    finally:
        # Cleanup
        if 'db_service' in locals():
            db_service.close()

if __name__ == "__main__":
    main()