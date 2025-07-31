#!/usr/bin/env python3
"""
Perf Pulse - Smart Test Insight Generator Launcher
Choose between Streamlit and Flask interfaces
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def print_banner():
    """Print the Perf Pulse banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║  🚀 Perf Pulse - Smart Test Insight Generator 🚀            ║
    ║                                                              ║
    ║  Advanced Performance Testing Analysis & Report Generation   ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = {
        'streamlit': 'streamlit',
        'flask': 'flask',
        'pandas': 'pandas',
        'plotly': 'plotly'
    }
    
    missing_packages = []
    
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {package} - Installed")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ All dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies. Please install manually:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
    
    return True

def run_streamlit():
    """Launch Streamlit interface"""
    print("\n🚀 Launching Streamlit Interface...")
    print("📊 Features:")
    print("   • Simple and intuitive interface")
    print("   • Quick data upload and analysis")
    print("   • Built-in visualizations")
    print("   • Easy report generation")
    
    try:
        # Start Streamlit
        process = subprocess.Popen([
            sys.executable, '-m', 'streamlit', 'run', 'frontend/streamlit_app.py',
            '--server.port', '8501',
            '--server.headless', 'true'
        ])
        
        # Wait a moment for Streamlit to start
        time.sleep(3)
        
        # Open browser
        webbrowser.open('http://localhost:8501')
        
        print("\n✅ Streamlit is running at: http://localhost:8501")
        print("🔄 Press Ctrl+C to stop the server")
        
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping Streamlit server...")
            process.terminate()
            
    except Exception as e:
        print(f"❌ Error launching Streamlit: {e}")

def run_flask():
    """Launch Flask interface"""
    print("\n🚀 Launching Flask Interface...")
    print("📊 Features:")
    print("   • Professional modern UI")
    print("   • Advanced drag-and-drop upload")
    print("   • Real-time charts and dashboards")
    print("   • Interactive visualizations")
    print("   • Mobile-responsive design")
    
    try:
        # Start Flask
        process = subprocess.Popen([
            sys.executable, 'flask_app/app.py'
        ])
        
        # Wait a moment for Flask to start
        time.sleep(3)
        
        # Open browser
        webbrowser.open('http://localhost:5000')
        
        print("\n✅ Flask is running at: http://localhost:5000")
        print("🔄 Press Ctrl+C to stop the server")
        
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping Flask server...")
            process.terminate()
            
    except Exception as e:
        print(f"❌ Error launching Flask: {e}")

def show_menu():
    """Show the main menu"""
    while True:
        print("\n" + "="*60)
        print("🎯 Choose Your Interface:")
        print("="*60)
        print("1. 🚀 Streamlit Interface (Simple & Quick)")
        print("2. 🎨 Flask Interface (Professional & Advanced)")
        print("3. 📊 Compare Features")
        print("4. 📁 View Demo Data")
        print("5. 🛠️  Check System Status")
        print("6. ❌ Exit")
        print("="*60)
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            run_streamlit()
        elif choice == '2':
            run_flask()
        elif choice == '3':
            compare_features()
        elif choice == '4':
            view_demo_data()
        elif choice == '5':
            check_system_status()
        elif choice == '6':
            print("\n👋 Thank you for using Perf Pulse!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-6.")

def compare_features():
    """Compare Streamlit vs Flask features"""
    print("\n" + "="*80)
    print("📊 FEATURE COMPARISON: Streamlit vs Flask")
    print("="*80)
    
    comparison = {
        "Interface Type": {
            "Streamlit": "Python-based, declarative",
            "Flask": "HTML/CSS/JS, component-based"
        },
        "Learning Curve": {
            "Streamlit": "Easy (Python only)",
            "Flask": "Moderate (HTML/CSS/JS)"
        },
        "UI Customization": {
            "Streamlit": "Limited",
            "Flask": "Full control"
        },
        "Real-time Updates": {
            "Streamlit": "Basic",
            "Flask": "Advanced (WebSocket)"
        },
        "Mobile Responsive": {
            "Streamlit": "Basic",
            "Flask": "Full responsive design"
        },
        "Performance": {
            "Streamlit": "Good for small datasets",
            "Flask": "Excellent for large datasets"
        },
        "Charts & Visualizations": {
            "Streamlit": "Built-in Plotly",
            "Flask": "Advanced (D3.js, Chart.js)"
        },
        "File Upload": {
            "Streamlit": "Basic upload",
            "Flask": "Drag-and-drop with progress"
        },
        "Professional Look": {
            "Streamlit": "Functional",
            "Flask": "Modern & Professional"
        }
    }
    
    for feature, options in comparison.items():
        print(f"\n🔹 {feature}:")
        print(f"   Streamlit: {options['Streamlit']}")
        print(f"   Flask:     {options['Flask']}")
    
    print("\n" + "="*80)
    print("💡 RECOMMENDATION:")
    print("   • Use Streamlit for: Quick analysis, simple dashboards")
    print("   • Use Flask for: Professional presentations, advanced features")
    print("="*80)

def view_demo_data():
    """Show available demo data"""
    print("\n📁 Available Demo Data:")
    print("="*40)
    
    demo_files = [
        ("demo_performance_data.xlsx", "Sample performance test data with response times, status codes, and endpoints"),
        ("ELIGIBLE_ACTION_50.csv", "JMeter format performance data"),
    ]
    
    for filename, description in demo_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✅ {filename}")
            print(f"   📄 {description}")
            print(f"   📏 Size: {size:,} bytes")
        else:
            print(f"❌ {filename} (not found)")
    
    print("\n💡 Tip: Upload these files to test the analysis features!")

def check_system_status():
    """Check system status and dependencies"""
    print("\n🔧 System Status Check:")
    print("="*40)
    
    # Check Python version
    python_version = sys.version_info
    print(f"🐍 Python: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check required packages
    packages = ['streamlit', 'flask', 'pandas', 'numpy', 'plotly']
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
    
    # Check demo files
    print("\n📁 Demo Files:")
    demo_files = ['demo_performance_data.xlsx', 'ELIGIBLE_ACTION_50.csv']
    for file in demo_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
    
    # Check directories
    print("\n📂 Project Structure:")
    dirs = ['backend', 'frontend', 'flask_app', 'data']
    for dir in dirs:
        if os.path.exists(dir):
            print(f"✅ {dir}/")
        else:
            print(f"❌ {dir}/")

def main():
    """Main launcher function"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again.")
        return
    
    print("\n✅ All systems ready!")
    
    # Show menu
    show_menu()

if __name__ == "__main__":
    main()