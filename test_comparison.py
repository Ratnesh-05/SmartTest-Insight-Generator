#!/usr/bin/env python3
"""
Test script for comparison report functionality
"""

import requests
import json
import os

def test_comparison_report():
    """Test the comparison report generation"""
    
    # Check if demo files exist
    file_a = "demo_performance_data.xlsx"
    file_b = "ELIGIBLE_ACTION_50.csv"
    
    if not os.path.exists(file_a):
        print(f"❌ Test file A not found: {file_a}")
        return False
        
    if not os.path.exists(file_b):
        print(f"❌ Test file B not found: {file_b}")
        return False
    
    print("✅ Test files found")
    
    # Test the comparison API
    url = "http://localhost:5000/api/reports/comparison"
    
    data = {
        "file_a_path": file_a,
        "file_b_path": file_b,
        "format": "pdf"
    }
    
    try:
        print("🔄 Testing comparison report generation...")
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            print("✅ Comparison report generated successfully!")
            
            # Save the PDF
            with open("test_comparison_report.pdf", "wb") as f:
                f.write(response.content)
            print("📄 PDF saved as test_comparison_report.pdf")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Comparison Report Functionality")
    print("=" * 50)
    
    success = test_comparison_report()
    
    if success:
        print("\n✅ Comparison report test completed successfully!")
    else:
        print("\n❌ Comparison report test failed!") 