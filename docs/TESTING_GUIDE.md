# Complete Testing Guide

## ✅ Port Configuration

**Current Port**: 8003 ✅
- `app/config.py`: PORT = 8003
- `.env.example`: PORT=8003

---

## 🚀 Step 1: Start the Application

### Terminal 1 (Run Server)
```bash
cd document-extraction-poc
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt

python -m app.main
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8003
INFO:     Application startup complete
```

---

## 🧪 Step 2: Run Tests

### Terminal 2 (Run Tests)
```bash
cd document-extraction-poc
python test_flow.py
```

**What it tests:**
1. ✅ Health check endpoint
2. ✅ Upload PDF from Dataset folder
3. ✅ Wait for processing
4. ✅ Retrieve results
5. ✅ Validate extracted data

---

## 📊 Expected Test Output

```
================================================================================
DOCUMENT EXTRACTION SYSTEM - FULL FLOW TEST
================================================================================

🔍 Looking for PDFs in Dataset/
✅ Found 3 PDF files

============================================================
TEST 1: Health Check
============================================================
Status: 200
Response: {'status': 'healthy', 'version': '0.1.0'}

============================================================
TEST 2: Upload & Process - Dataset/PS_New_Aisah.pdf
============================================================
📤 Uploading: Dataset/PS_New_Aisah.pdf
Status: 200
Response: {
  "status": "processing",
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "File uploaded successfully. Processing started."
}
✅ Upload ID: 550e8400-e29b-41d4-a716-446655440000

⏳ Waiting for processing...
  [1s] Status: processing
  [2s] Status: processing
  [3s] Status: processing
  [4s] Status: completed
✅ Processing completed!

📊 Getting results...

✅ Results Retrieved:
   File Type: pdf
   Total Documents: 1

   Document 1:
     Type: payslip
     Confidence: 0.95
     Extracted Data:
       name: SITI AISAH BINTI GHAZALI
       id_number: 790712-03-5260
       gross_income: 16580.00
       net_income: 12500.20
       total_deduction: 4079.80
       month_year: 11/2025

   Summary:
     Payslips: 1
     Bank Statements: 0
     Average Confidence: 0.95

================================================================================
TEST SUMMARY
================================================================================
✅ PASSED: Dataset/PS_New_Aisah.pdf
✅ PASSED: Dataset/CIMB-Siti Aisah.pdf
✅ PASSED: Dataset/CIMB-Siti Aisah 2.pdf

Total: 3/3 tests passed

================================================================================
✅ ALL TESTS PASSED!
================================================================================
```

---

## 🌐 Manual Testing with Browser

### 1. Health Check
```
GET http://localhost:8003/health
```

### 2. API Documentation
```
http://localhost:8003/docs
```

### 3. Upload Document
```
POST http://localhost:8003/api/upload
Body: multipart/form-data with file
```

### 4. Check Status
```
GET http://localhost:8003/api/status/{upload_id}
```

### 5. Get Results
```
GET http://localhost:8003/api/result/{upload_id}
```

---

## 📁 Files Created During Testing

```
uploads/
├── raw/
│   └── {upload_id}.pdf          ← Uploaded PDF
└── processed/
    └── {upload_id}/
        ├── page_1.png           ← Converted images
        ├── page_2.png
        └── page_3.png

output/
├── json/
│   └── {upload_id}.json         ← Extraction results
└── logs/
    └── app.log                  ← Processing logs
```

---

## 🔍 Processing Flow Verification

### 1. Check Logs
```bash
tail -f document-extraction-poc/output/logs/app.log
```

### 2. Check Results
```bash
cat document-extraction-poc/output/json/{upload_id}.json
```

### 3. Check Uploaded Files
```bash
ls -la document-extraction-poc/uploads/raw/
ls -la document-extraction-poc/uploads/processed/
```

---

## ⚠️ Troubleshooting

### Issue: Port 8003 already in use
```bash
# Find process using port 8003
netstat -ano | findstr :8003  # Windows
lsof -i :8003                 # Linux/Mac

# Kill process
taskkill /PID {PID} /F        # Windows
kill -9 {PID}                 # Linux/Mac
```

### Issue: OCR not working
```bash
# Install PaddleOCR
pip install paddleocr

# Or use EasyOCR
pip install easyocr

# Or use Tesseract
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# Linux: sudo apt-get install tesseract-ocr
# Mac: brew install tesseract
```

### Issue: PyMuPDF not installed
```bash
pip install PyMuPDF
```

### Issue: Processing takes too long
- First run downloads OCR models (~200MB)
- Subsequent runs are faster
- Check logs for progress

---

## 📊 Performance Metrics

| Operation | Time | Notes |
|-----------|------|-------|
| Upload | <1s | File save |
| PDF → Images | 2-5s | Depends on page count |
| OCR | 5-15s | First run slower (model download) |
| Classification | <1s | Keyword matching |
| Extraction | <1s | Pattern matching |
| Validation | <1s | Format check |
| **Total** | **10-25s** | First run, single page |

---

## ✅ Verification Checklist

- [ ] Server running on port 8003
- [ ] Health check returns 200
- [ ] Upload endpoint accepts files
- [ ] Processing completes successfully
- [ ] Results contain extracted data
- [ ] Confidence score >= 0.95
- [ ] Files saved to correct directories
- [ ] Logs generated
- [ ] All 3 test PDFs processed

---

## 🎯 Next Steps

1. ✅ Start server: `python -m app.main`
2. ✅ Run tests: `python test_flow.py`
3. ✅ Check results: `cat output/json/{upload_id}.json`
4. ✅ Review logs: `tail -f output/logs/app.log`

---

## 📞 Support

If tests fail:
1. Check server is running
2. Check port 8003 is available
3. Check all dependencies installed
4. Check logs for errors
5. Verify Dataset folder has PDFs

**Happy Testing!** 🚀
