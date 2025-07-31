import requests
import json

def test_pdf_generation():
    # First upload a file to get data
    with open('demo_performance_data.xlsx', 'rb') as f:
        files = {'file': f}
        response = requests.post('http://127.0.0.1:5000/api/upload', files=files)
    
    if response.status_code == 200:
        upload_data = response.json()
        print("✅ Upload successful")
        
        # Now test PDF generation
        report_data = {
            'type': 'executive',
            'format': 'pdf',
            'data': upload_data['data']
        }
        
        response = requests.post('http://127.0.0.1:5000/api/reports/generate', 
                               json=report_data)
        
        print(f"PDF Status: {response.status_code}")
        print(f"PDF Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            # Save the PDF
            with open('test_report.pdf', 'wb') as f:
                f.write(response.content)
            print("✅ PDF saved as test_report.pdf")
        else:
            print(f"❌ PDF generation failed: {response.text}")
    else:
        print(f"❌ Upload failed: {response.text}")

if __name__ == "__main__":
    test_pdf_generation() 