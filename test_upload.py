import requests
import json

def test_upload():
    try:
        # Test with demo Excel file
        with open('demo_performance_data.xlsx', 'rb') as f:
            files = {'file': f}
            response = requests.post('http://127.0.0.1:5000/api/upload', files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Upload successful!")
            print(f"Records processed: {data.get('data', {}).get('total_records', 0)}")
        else:
            print("❌ Upload failed!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_upload() 