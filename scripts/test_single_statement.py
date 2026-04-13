"""
Test a single bank statement and wait for results
"""
import sys
import os
import requests
import json
import time

def test_statement(file_path, bank_name):
    """Test a single bank statement"""
    print(f"\n{'='*80}")
    print(f"Testing: {bank_name}")
    print(f"File: {file_path}")
    print(f"{'='*80}\n")
    
    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        return None
    
    try:
        # Upload file
        print("[1/3] Uploading file...")
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'application/pdf')}
            response = requests.post("http://localhost:8004/api/upload", files=files, timeout=120)
        
        if response.status_code != 200:
            print(f"[ERROR] Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        upload_data = response.json()
        upload_id = upload_data.get('upload_id')
        print(f"[OK] Uploaded! ID: {upload_id}")
        
        # Wait for processing
        print("\n[2/3] Processing (this may take 30-60 seconds)...")
        max_wait = 120  # 2 minutes max
        waited = 0
        
        while waited < max_wait:
            time.sleep(3)
            waited += 3
            
            try:
                result_response = requests.get(f"http://localhost:8004/api/result/{upload_id}", timeout=10)
                
                if result_response.status_code == 200:
                    result = result_response.json()
                    print(f"[OK] Processing complete! (took {waited}s)")
                    break
                elif result_response.status_code == 202:
                    if waited % 15 == 0:  # Print every 15 seconds
                        print(f"  Still processing... ({waited}s elapsed)")
                    continue
                else:
                    print(f"[ERROR] Result error: {result_response.status_code}")
                    return None
            except Exception as e:
                if waited % 15 == 0:
                    print(f"  Waiting... ({waited}s elapsed)")
                continue
        else:
            print(f"[ERROR] Timeout after {max_wait}s")
            return None
        
        # Display results
        print(f"\n[3/3] Results:")
        print(f"{'='*80}")
        
        if result.get('documents'):
            doc = result['documents'][0]
            extracted = doc.get('extracted_data', {})
            
            print(f"\nBank Detected: {extracted.get('detected_bank', 'N/A')}")
            print(f"Confidence Score: {doc.get('confidence_score', 0)}")
            print(f"Pages: {doc.get('page_count', 0)}")
            print(f"Merged: {doc.get('is_merged', False)}")
            
            print(f"\nExtracted Fields:")
            print(f"{'-'*80}")
            
            for key, value in extracted.items():
                if key in ['page_count', 'pages', 'detected_bank', 'bank_detection_confidence']:
                    continue
                
                status = "[OK]  " if value else "[MISS]"
                print(f"{status} {key:25s}: {value}")
            
            print(f"{'-'*80}")
            
            # Count fields
            total_fields = len([k for k in extracted.keys() if k not in ['page_count', 'pages', 'detected_bank', 'bank_detection_confidence']])
            filled_fields = len([v for k, v in extracted.items() if v and k not in ['page_count', 'pages', 'detected_bank', 'bank_detection_confidence']])
            
            print(f"\nFields Extracted: {filled_fields}/{total_fields} ({filled_fields*100//total_fields}%)")
            print(f"{'='*80}\n")
        
        return result
            
    except Exception as e:
        print(f"[ERROR] Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_single_statement.py <file_path> <bank_name>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    bank_name = sys.argv[2]
    
    result = test_statement(file_path, bank_name)
    
    if result:
        # Save result
        output_file = f"test_result_{bank_name.replace(' ', '_').lower()}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Result saved to: {output_file}")
    else:
        print("Test failed!")
        sys.exit(1)
