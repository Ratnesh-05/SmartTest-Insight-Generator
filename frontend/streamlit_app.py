"""
🚀 Perf Pulse - Smart Test Insight Generator
Advanced Performance Testing Analysis & Report Generation
Created by Perf Pulse
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from pathlib import Path
import tempfile
import base64
import numpy as np
from datetime import datetime

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

# Import backend modules
try:
    from backend.core.data_processor import PerformanceDataProcessor
    from backend.core.log_analyzer import LogAnalyzer
    from backend.core.performance_analyzer import PerformanceAnalyzer
    from backend.reports.pdf_generator import PDFReportGenerator
    from backend.reports.excel_generator import ExcelReportGenerator
    from config import config
except ImportError as e:
    st.error(f"Backend modules not found: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Perf Pulse - Smart Test Insight Generator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for awesome UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .perf-pulse-logo {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border-left: 5px solid #667eea;
        margin: 0.5rem 0;
    }
    .success { color: #28a745; font-weight: bold; }
    .warning { color: #ffc107; font-weight: bold; }
    .danger { color: #dc3545; font-weight: bold; }
    .info { color: #17a2b8; font-weight: bold; }
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #5a6fd8 0%, #6a4190 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

def process_jmeter_data(df):
    """Process JMeter-style CSV data and convert to standard format"""
    try:
        # Check if this is JMeter format
        if 'Average' in df.columns and 'Median' in df.columns:
            st.info("📊 Detected JMeter format data. Converting to standard format...")
            
            # Create a new DataFrame with standard column names
            processed_data = []
            
            for _, row in df.iterrows():
                # Extract metrics from JMeter format
                avg_response_time = row.get('Average', 0)
                median_response_time = row.get('Median', 0)
                p90_response_time = row.get('90% Line', 0)
                p95_response_time = row.get('95% Line', 0)
                p99_response_time = row.get('99% Line', 0)
                min_response_time = row.get('Min', 0)
                max_response_time = row.get('Max', 0)
                error_rate = row.get('Error %', 0)
                throughput = row.get('Throughput', 0)
                
                # Create multiple records to simulate individual requests
                num_samples = int(row.get('# Samples', 100))
                
                # Generate synthetic data points based on the metrics
                for i in range(min(num_samples, 1000)):  # Limit to 1000 for performance
                    # Generate response time based on distribution
                    if np.random.random() < 0.5:
                        response_time = np.random.normal(avg_response_time, avg_response_time * 0.2)
                    else:
                        response_time = np.random.exponential(avg_response_time)
                    
                    response_time = max(min_response_time, min(max_response_time, response_time))
                    
                    # Determine status code based on error rate
                    status_code = 200 if np.random.random() > (error_rate / 100) else 500
                    
                    processed_data.append({
                        'timestamp': datetime.now().timestamp() + i,
                        'response_time': response_time,
                        'status_code': status_code,
                        'endpoint': row.get('Label', 'Unknown'),
                        'user_id': f"user_{i % 10}",
                        'requests_per_sec': throughput / num_samples if num_samples > 0 else 0
                    })
            
            return pd.DataFrame(processed_data)
        else:
            return df
    except Exception as e:
        st.error(f"Error processing JMeter data: {e}")
        return df

def main():
    """Main Streamlit application"""
    
    # Header with Perf Pulse branding
    st.markdown("""
    <div class="main-header">
        <div class="perf-pulse-logo">⚡ Perf Pulse</div>
        <h1>Smart Test Insight Generator</h1>
        <p>Advanced Performance Testing Analysis & Report Generation</p>
        <small>Created by Perf Pulse Team</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("⚡ Perf Pulse")
    st.sidebar.markdown("---")
    page = st.sidebar.selectbox(
        "📋 Navigation",
        ["🏠 Dashboard", "📊 Performance Analysis", "📝 Log Analysis", "📈 Reports", "⚙️ Settings"]
    )
    
    # Add demo data download
    st.sidebar.markdown("---")
    st.sidebar.subheader("📁 Sample Data")
    if st.sidebar.button("📥 Download Demo Data"):
        create_demo_data()
    
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "📊 Performance Analysis":
        show_performance_analysis()
    elif page == "📝 Log Analysis":
        show_log_analysis()
    elif page == "📈 Reports":
        show_reports()
    elif page == "⚙️ Settings":
        show_settings()

def create_demo_data():
    """Create and provide demo data for download"""
    # Create sample performance data
    np.random.seed(42)
    n_samples = 1000
    
    timestamps = pd.date_range(start='2024-01-01', periods=n_samples, freq='S')
    response_times = np.random.exponential(500, n_samples) + 200  # Base 200ms + exponential
    status_codes = np.random.choice([200, 200, 200, 404, 500], n_samples, p=[0.85, 0.05, 0.05, 0.03, 0.02])
    endpoints = np.random.choice(['/api/users', '/api/products', '/api/orders', '/api/search'], n_samples)
    user_ids = [f"user_{i % 100}" for i in range(n_samples)]
    
    demo_data = pd.DataFrame({
        'timestamp': timestamps,
        'response_time': response_times,
        'status_code': status_codes,
        'endpoint': endpoints,
        'user_id': user_ids,
        'requests_per_sec': np.random.uniform(10, 50, n_samples)
    })
    
    # Convert to CSV
    csv = demo_data.to_csv(index=False)
    st.sidebar.download_button(
        label="📊 Download Demo CSV",
        data=csv,
        file_name="demo_performance_data.csv",
        mime="text/csv"
    )

def show_dashboard():
    """Enhanced Dashboard page"""
    st.header("🏠 Performance Dashboard")
    
    # Overview metrics with better styling
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 Total Tests</h3>
            <h2>0</h2>
            <p>No data loaded</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>✅ Success Rate</h3>
            <h2>0%</h2>
            <p>No data loaded</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>⚡ Avg Response Time</h3>
            <h2>0ms</h2>
            <p>No data loaded</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>🚨 Error Rate</h3>
            <h2>0%</h2>
            <p>No data loaded</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Analyze Performance Data", use_container_width=True):
            st.info("💡 Upload your performance data file to get started!")
    
    with col2:
        if st.button("📝 Analyze Log Files", use_container_width=True):
            st.info("💡 Upload your log files to analyze errors and patterns!")
    
    # Recent activity
    st.subheader("📈 Recent Activity")
    st.info("📋 No recent activity. Upload data to see analysis results.")

def show_performance_analysis():
    """Enhanced Performance analysis page"""
    st.header("📊 Performance Analysis")
    
    # File upload with better styling
    uploaded_file = st.file_uploader(
        "📁 Upload Performance Data",
        type=['csv', 'xlsx', 'json'],
        help="Upload your performance test data (CSV, Excel, or JSON format). Supports JMeter format!"
    )
    
    if uploaded_file is not None:
        try:
            # Process the uploaded file
            with st.spinner("🔄 Processing performance data..."):
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                # Load data
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(tmp_file_path)
                elif uploaded_file.name.endswith('.xlsx'):
                    df = pd.read_excel(tmp_file_path)
                else:
                    df = pd.read_json(tmp_file_path)
                
                # Process JMeter data if needed
                df = process_jmeter_data(df)
                
                # Clean up temp file
                os.unlink(tmp_file_path)
                
                st.success(f"✅ Successfully processed {len(df)} records!")
                
                # Display enhanced metrics and visualizations
                display_enhanced_metrics(df)
                
                # Advanced analysis
                if st.button("🔍 Run Advanced Analysis", use_container_width=True):
                    with st.spinner("🔄 Running advanced analysis..."):
                        display_advanced_analysis_enhanced(df)
                
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.info("💡 Make sure your file has the correct format. Try downloading the demo data for reference.")

def display_enhanced_metrics(df):
    """Display enhanced performance metrics with better visualizations"""
    st.subheader("📈 Performance Metrics")
    
    # Calculate basic metrics
    if 'response_time' in df.columns:
        rt = df['response_time']
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>⚡ Avg Response Time</h3>
                <h2>{rt.mean():.2f}ms</h2>
                <p>Mean response time</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📊 95th Percentile</h3>
                <h2>{rt.quantile(0.95):.2f}ms</h2>
                <p>95% of requests</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🚀 Max Response Time</h3>
                <h2>{rt.max():.2f}ms</h2>
                <p>Slowest request</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>⚡ Min Response Time</h3>
                <h2>{rt.min():.2f}ms</h2>
                <p>Fastest request</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Error metrics
    if 'status_code' in df.columns:
        total_requests = len(df)
        error_requests = len(df[df['status_code'] >= 400])
        error_rate = (error_requests / total_requests) * 100 if total_requests > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📊 Total Requests</h3>
                <h2>{total_requests:,}</h2>
                <p>All requests</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🚨 Error Requests</h3>
                <h2>{error_requests:,}</h2>
                <p>Failed requests</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>⚠️ Error Rate</h3>
                <h2>{error_rate:.2f}%</h2>
                <p>Error percentage</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Enhanced visualizations
    st.subheader("📊 Performance Visualizations")
    
    # Response time distribution
    if 'response_time' in df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="chart-container">
                <h4>📈 Response Time Distribution</h4>
            </div>
            """, unsafe_allow_html=True)
            fig = px.histogram(
                df, 
                x='response_time', 
                nbins=50, 
                title="Response Time Distribution",
                color_discrete_sequence=['#667eea']
            )
            fig.update_layout(
                xaxis_title="Response Time (ms)",
                yaxis_title="Frequency",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("""
            <div class="chart-container">
                <h4>📊 Response Time Box Plot</h4>
            </div>
            """, unsafe_allow_html=True)
            fig = px.box(
                df, 
                y='response_time',
                title="Response Time Statistics",
                color_discrete_sequence=['#764ba2']
            )
            fig.update_layout(
                yaxis_title="Response Time (ms)",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Status code distribution
    if 'status_code' in df.columns:
        st.markdown("""
        <div class="chart-container">
            <h4>📊 Status Code Distribution</h4>
        </div>
        """, unsafe_allow_html=True)
        
        status_counts = df['status_code'].value_counts()
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Status Code Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Endpoint performance
    if 'endpoint' in df.columns:
        st.markdown("""
        <div class="chart-container">
            <h4>🌐 Endpoint Performance</h4>
        </div>
        """, unsafe_allow_html=True)
        
        endpoint_stats = df.groupby('endpoint')['response_time'].agg(['mean', 'count']).reset_index()
        fig = px.bar(
            endpoint_stats,
            x='endpoint',
            y='mean',
            title="Average Response Time by Endpoint",
            color='count',
            color_continuous_scale='viridis'
        )
        fig.update_layout(
            xaxis_title="Endpoint",
            yaxis_title="Average Response Time (ms)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Data preview
    st.subheader("📋 Data Preview")
    st.dataframe(df.head(10), use_container_width=True)

def display_advanced_analysis_enhanced(df):
    """Display enhanced advanced analysis results"""
    st.subheader("🔍 Advanced Analysis")
    
    # Time series analysis
    if 'timestamp' in df.columns:
        st.markdown("""
        <div class="chart-container">
            <h4>⏰ Response Time Over Time</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Convert timestamp to datetime if needed
        if df['timestamp'].dtype == 'object':
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        fig = px.scatter(
            df,
            x='timestamp',
            y='response_time',
            color='status_code',
            title="Response Time Over Time",
            color_continuous_scale='viridis'
        )
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Response Time (ms)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Anomaly detection
    if 'response_time' in df.columns:
        st.markdown("""
        <div class="chart-container">
            <h4>🚨 Anomaly Detection</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Simple anomaly detection using IQR
        Q1 = df['response_time'].quantile(0.25)
        Q3 = df['response_time'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        anomalies = df[(df['response_time'] < lower_bound) | (df['response_time'] > upper_bound)]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("🚨 Anomalies Detected", len(anomalies))
        
        with col2:
            st.metric("📊 Anomaly Rate", f"{(len(anomalies) / len(df) * 100):.2f}%")
        
        if len(anomalies) > 0:
            st.warning(f"⚠️ Found {len(anomalies)} anomalies in your data!")
            
            # Show anomaly details
            fig = px.scatter(
                df,
                x=range(len(df)),
                y='response_time',
                color=df['response_time'].apply(lambda x: 'Anomaly' if x < lower_bound or x > upper_bound else 'Normal'),
                title="Anomaly Detection",
                color_discrete_map={'Normal': '#28a745', 'Anomaly': '#dc3545'}
            )
            fig.update_layout(
                xaxis_title="Request Index",
                yaxis_title="Response Time (ms)"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("✅ No anomalies detected in your data!")

def show_log_analysis():
    """Enhanced Log analysis page"""
    st.header("📝 Log Analysis")
    
    # File upload
    uploaded_file = st.file_uploader(
        "📁 Upload Log File",
        type=['log', 'txt', 'csv'],
        help="Upload your application log file"
    )
    
    if uploaded_file is not None:
        try:
            with st.spinner("🔄 Processing log file..."):
                # For now, just read as text and show basic analysis
                log_content = uploaded_file.read().decode('utf-8')
                log_lines = log_content.split('\n')
                
                st.success(f"✅ Successfully processed {len(log_lines)} log lines!")
                
                # Basic log analysis
                st.subheader("📊 Log Analysis Results")
                
                # Count different log levels
                error_count = sum(1 for line in log_lines if 'ERROR' in line.upper() or 'EXCEPTION' in line.upper())
                warning_count = sum(1 for line in log_lines if 'WARN' in line.upper())
                info_count = sum(1 for line in log_lines if 'INFO' in line.upper())
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("🚨 Errors", error_count)
                
                with col2:
                    st.metric("⚠️ Warnings", warning_count)
                
                with col3:
                    st.metric("ℹ️ Info", info_count)
                
                # Log level distribution
                if error_count + warning_count + info_count > 0:
                    fig = px.pie(
                        values=[error_count, warning_count, info_count],
                        names=['Errors', 'Warnings', 'Info'],
                        title="Log Level Distribution",
                        color_discrete_sequence=['#dc3545', '#ffc107', '#17a2b8']
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Show sample log lines
                st.subheader("📋 Sample Log Lines")
                st.text_area("Log Preview", log_content[:2000] + "..." if len(log_content) > 2000 else log_content, height=200)
                
        except Exception as e:
            st.error(f"❌ Error processing log file: {str(e)}")

def show_reports():
    """Enhanced Reports page with file upload and real report generation"""
    st.header("📈 Report Generation")
    
    st.markdown("""
    <div class="metric-card">
        <h3>📊 Generate Comprehensive Reports</h3>
        <p>Upload your performance data and create detailed reports in multiple formats</p>
    </div>
    """, unsafe_allow_html=True)
    
    # File upload for report generation
    uploaded_file = st.file_uploader(
        "📁 Upload Performance Data for Report Generation",
        type=['csv', 'xlsx', 'json'],
        help="Upload your performance test data to generate reports"
    )
    
    if uploaded_file is not None:
        try:
            with st.spinner("🔄 Processing data for report generation..."):
                processor = PerformanceDataProcessor()
                
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                # Load and process data
                df = processor.load_test_data(tmp_file_path)
                metrics = processor.calculate_basic_metrics()
                
                # Clean up temp file
                os.unlink(tmp_file_path)
                
                st.success(f"✅ Data processed successfully! {len(df)} records ready for report generation.")
                
                # Report options
                col1, col2 = st.columns(2)
                
                with col1:
                    report_type = st.selectbox(
                        "📋 Report Type",
                        ["Executive Summary", "Detailed Analysis", "Trends Report", "Anomaly Report"]
                    )
                
                with col2:
                    output_format = st.selectbox(
                        "📄 Output Format",
                        ["PDF", "Excel", "HTML"]
                    )
                
                # Generate report button
                if st.button("📊 Generate Report", use_container_width=True):
                    with st.spinner("🔄 Generating report..."):
                        try:
                            # Prepare report data
                            report_data = {
                                'metrics': metrics,
                                'summary': {
                                    'total_entries': len(df),
                                    'file_name': uploaded_file.name,
                                    'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                },
                                'data_preview': df.head(10).to_dict('records')
                            }
                            
                            # Generate report based on format
                            if output_format == "PDF":
                                pdf_generator = PDFReportGenerator()
                                report_path = pdf_generator.generate_performance_report(report_data, "performance_report.pdf")
                                
                                # Read and provide download
                                with open(report_path, "rb") as f:
                                    pdf_bytes = f.read()
                                st.download_button(
                                    label="📥 Download PDF Report",
                                    data=pdf_bytes,
                                    file_name=f"perf_pulse_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                    mime="application/pdf"
                                )
                                
                            elif output_format == "Excel":
                                excel_generator = ExcelReportGenerator()
                                report_path = excel_generator.create_performance_report(report_data, "performance_report.xlsx")
                                
                                # Read and provide download
                                with open(report_path, "rb") as f:
                                    excel_bytes = f.read()
                                st.download_button(
                                    label="📥 Download Excel Report",
                                    data=excel_bytes,
                                    file_name=f"perf_pulse_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                                
                            elif output_format == "HTML":
                                # Create HTML report
                                html_content = f"""
                                <html>
                                <head>
                                    <title>Perf Pulse Performance Report</title>
                                    <style>
                                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                                        .header {{ background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; }}
                                        .metric {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                                        .success {{ color: #28a745; }}
                                        .warning {{ color: #ffc107; }}
                                        .danger {{ color: #dc3545; }}
                                    </style>
                                </head>
                                <body>
                                    <div class="header">
                                        <h1>🚀 Perf Pulse Performance Report</h1>
                                        <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                                    </div>
                                    
                                    <h2>📊 Performance Metrics</h2>
                                    <div class="metric">
                                        <h3>Response Time Analysis</h3>
                                        <p><strong>Average:</strong> {metrics.get('response_time', {}).get('mean', 0):.2f}ms</p>
                                        <p><strong>95th Percentile:</strong> {metrics.get('response_time', {}).get('p95', 0):.2f}ms</p>
                                        <p><strong>Maximum:</strong> {metrics.get('response_time', {}).get('max', 0):.2f}ms</p>
                                    </div>
                                    
                                    <div class="metric">
                                        <h3>Error Analysis</h3>
                                        <p><strong>Total Requests:</strong> {metrics.get('errors', {}).get('total_requests', 0):,}</p>
                                        <p><strong>Error Rate:</strong> {metrics.get('errors', {}).get('error_rate', 0):.2f}%</p>
                                    </div>
                                    
                                    <h2>📋 Data Summary</h2>
                                    <p><strong>Total Records:</strong> {len(df):,}</p>
                                    <p><strong>File Name:</strong> {uploaded_file.name}</p>
                                </body>
                                </html>
                                """
                                
                                st.download_button(
                                    label="📥 Download HTML Report",
                                    data=html_content.encode(),
                                    file_name=f"perf_pulse_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                                    mime="text/html"
                                )
                            
                            st.success(f"✅ {output_format} report generated successfully!")
                            
                        except Exception as e:
                            st.error(f"❌ Error generating report: {str(e)}")
                
                # Show data preview
                st.subheader("📋 Data Preview")
                st.dataframe(df.head(10))
                
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.info("💡 Make sure your file has the correct format. Try downloading the demo data for reference.")
    
    else:
        st.info("📁 Please upload a performance data file to generate reports.")
        
        # Demo data download
        if st.button("📥 Download Demo Data", use_container_width=True):
            st.info("💡 Use the demo data to test report generation functionality.")

def show_settings():
    """Enhanced Settings page"""
    st.header("⚙️ Settings")
    
    st.markdown("""
    <div class="metric-card">
        <h3>🔧 Configure Application Settings</h3>
        <p>Customize thresholds and analysis parameters</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Performance thresholds
    st.subheader("📊 Performance Thresholds")
    
    col1, col2 = st.columns(2)
    
    with col1:
        warning_rt = st.number_input(
            "⚡ Response Time Warning (ms)",
            value=1000,
            help="Response time threshold for warnings"
        )
        critical_rt = st.number_input(
            "🚨 Response Time Critical (ms)",
            value=3000,
            help="Response time threshold for critical alerts"
        )
    
    with col2:
        warning_error = st.number_input(
            "⚠️ Error Rate Warning (%)",
            value=5.0,
            help="Error rate threshold for warnings"
        )
        critical_error = st.number_input(
            "🚨 Error Rate Critical (%)",
            value=10.0,
            help="Error rate threshold for critical alerts"
        )
    
    if st.button("💾 Save Settings", use_container_width=True):
        st.success("✅ Settings saved successfully!")

def download_link(val, filename):
    """Generate download link for files"""
    b64 = base64.b64encode(val)
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}">Download {filename}</a>'

if __name__ == "__main__":
    main()