import requests
import time

file_path = "Dataset/Bank Statements/CIMB-Siti Aisah.pdf"

print(f"Testing: {file_path}")

with open(file_path, 'rb') as f:
    files = {'file': ('test.pdf', f, 'application/pdf')}
    response = requests.post("http://localhost:8000/api/upload", files=files)
    
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    data = response.json()
    upload_id = data.get('upload_id')
    print(f"\nUpload ID: {upload_id}")
    
    print("\nWaiting for result...")
    time.sleep(10)
    
    result = requests.get(f"http://localhost:8000/api/result/{upload_id}")
    print(f"\nResult Status: {result.status_code}")
    if result.status_code == 200:
        print(f"Result: {result.json()}")
