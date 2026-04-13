"""
Test all bank statements from Dataset folder and capture results
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
import json
from pathlib import Path
import time

# API endpoint
API_UPLOAD_URL = "http://localhost:8004/api/upload"
API_RESULT_URL = "http://localhost:8004/api/result"

# Bank statements to test
BANK_STATEMENTS = [
    "Dataset/Bank Statements/CIMB-Siti Aisah.pdf",
    "Dataset/Bank Statements/CIMB-Siti Aisah 2.pdf",
    "Dataset/Bank Statements/test ocr bank statement bank islam.pdf",
    "Dataset/Bank Statements/test ocr bank statement bsn.pdf",
    "Dataset/Bank Statements/test ocr bank statement public bank.pdf"
]

def test_statement(file_path):
    """Test a single bank statement"""
    print(f"\n{'='*80}")
    print(f"Testing: {file_path}")
    print(f"{'='*80}")
    
    if not os.path.exists(file_path):
        print(f"[FAIL] File not found: {file_path}")
        return None
    
    try:
        # Upload file
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'application/pdf')}
            response = requests.post(API_UPLOAD_URL, files=files, timeout=120)
        
        if response.status_code != 200:
            print(f"[FAIL] Upload Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        upload_data = response.json()
        upload_id = upload_data.get('upload_id')
        print(f"[OK] Uploaded! ID: {upload_id}")
        
        # Wait for processing
        print("[WAIT] Processing...")
        max_wait = 60  # 60 seconds
        waited = 0
        while waited < max_wait:
            time.sleep(2)
            waited += 2
            
            try:
                result_response = requests.get(f"{API_RESULT_URL}/{upload_id}", timeout=10)
                if result_response.status_code == 200:
                    result = result_response.json()
                    break
                elif result_response.status_code == 202:
                    print(f"  Still processing... ({waited}s)")
                    continue
                else:
                    print(f"[FAIL] Result Error: {result_response.status_code}")
                    return None
            except Exception as e:
                print(f"  Waiting... ({waited}s)")
                continue
        else:
            print(f"[FAIL] Timeout after {max_wait}s")
            return None
        
        print(f"[OK] Processing Complete!")
        print(f"\nResponse Summary:")
        print(f"  - Total Documents: {result.get('total_documents', 0)}")
        print(f"  - Average Confidence: {result.get('summary', {}).get('average_confidence', 0)}")
        
        if result.get('documents'):
            doc = result['documents'][0]
            print(f"\nExtracted Data:")
            extracted = doc.get('extracted_data', {})
            for key, value in extracted.items():
                if key in ['page_count', 'pages']:
                    continue
                status = "[OK]" if value else "[MISS]"
                print(f"  {status} {key}: {value}")
            
            print(f"\nMetadata:")
            print(f"  - Confidence Score: {doc.get('confidence_score', 0)}")
            print(f"  - Text Length: {doc.get('text_length', 0)}")
            print(f"  - Is Merged: {doc.get('is_merged', False)}")
            print(f"  - Pages: {doc.get('page_count', 0)}")
        
        return result
            
    except Exception as e:
        print(f"[FAIL] Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("="*80)
    print("BANK STATEMENT EXTRACTION TEST SUITE")
    print("="*80)
    
    results = []
    
    for statement in BANK_STATEMENTS:
        result = test_statement(statement)
        if result:
            results.append({
                'file': statement,
                'result': result
            })
        time.sleep(2)  # Wait between requests
    
    # Save all results
    output_file = "test_results_bank_statements.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"[OK] All results saved to: {output_file}")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
