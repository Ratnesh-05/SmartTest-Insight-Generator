import requests
import json

def test_report_generation():
    try:
        # First upload a file to get data
        print("1. Uploading test file...")
        with open('demo_performance_data.xlsx', 'rb') as f:
            files = {'file': f}
            response = requests.post('http://127.0.0.1:5000/api/upload', files=files)
        
        if response.status_code != 200:
            print(f"Upload failed: {response.text}")
            return
        
        upload_data = response.json()
        print("✅ Upload successful!")
        
        # Test PDF report generation
        print("\n2. Testing PDF report generation...")
        pdf_response = requests.post('http://127.0.0.1:5000/api/reports/generate', 
                                   json={
                                       'data': upload_data['data'],
                                       'type': 'executive',
                                       'format': 'pdf'
                                   })
        
        print(f"PDF Status: {pdf_response.status_code}")
        if pdf_response.status_code == 200:
            with open('test_report.pdf', 'wb') as f:
                f.write(pdf_response.content)
            print("✅ PDF report generated: test_report.pdf")
        else:
            print(f"❌ PDF generation failed: {pdf_response.text}")
        
        # Test Excel report generation
        print("\n3. Testing Excel report generation...")
        excel_response = requests.post('http://127.0.0.1:5000/api/reports/generate', 
                                     json={
                                         'data': upload_data['data'],
                                         'type': 'detailed',
                                         'format': 'excel'
                                     })
        
        print(f"Excel Status: {excel_response.status_code}")
        if excel_response.status_code == 200:
            with open('test_report.xlsx', 'wb') as f:
                f.write(excel_response.content)
            print("✅ Excel report generated: test_report.xlsx")
        else:
            print(f"❌ Excel generation failed: {excel_response.text}")
        
        # Test HTML report generation
        print("\n4. Testing HTML report generation...")
        html_response = requests.post('http://127.0.0.1:5000/api/reports/generate', 
                                    json={
                                        'data': upload_data['data'],
                                        'type': 'trends',
                                        'format': 'html'
                                    })
        
        print(f"HTML Status: {html_response.status_code}")
        if html_response.status_code == 200:
            html_data = html_response.json()
            with open('test_report.html', 'w', encoding='utf-8') as f:
                f.write(html_data['html_content'])
            print("✅ HTML report generated: test_report.html")
        else:
            print(f"❌ HTML generation failed: {html_response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_report_generation()