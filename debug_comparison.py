#!/usr/bin/env python3
"""
Debug script for comparison report functionality
"""

import requests
import json
import os

def debug_comparison():
    """Debug the comparison report step by step"""
    
    # Test files
    file_a = "demo_performance_data.xlsx"
    file_b = "ELIGIBLE_ACTION_50.csv"
    
    print(f"📁 File A exists: {os.path.exists(file_a)}")
    print(f"📁 File B exists: {os.path.exists(file_b)}")
    
    # Test the health endpoint first
    try:
        response = requests.get("http://localhost:5000/api/health")
        print(f"✅ Health check: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test with minimal data
    data = {
        "file_a_path": file_a,
        "file_b_path": file_b,
        "format": "pdf"
    }
    
    print(f"📤 Sending data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post("http://localhost:5000/api/reports/comparison", json=data)
        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Comparison report generated successfully!")
            with open("debug_comparison_report.pdf", "wb") as f:
                f.write(response.content)
            print("📄 PDF saved as debug_comparison_report.pdf")
        else:
            print(f"❌ Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("🔍 Debugging Comparison Report")
    print("=" * 40)
    debug_comparison() 