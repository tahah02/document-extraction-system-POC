# Document Extraction System - Project Flow

## Overview
This project extracts structured data from PDF documents (Payslips and Bank Statements) using OCR and pattern matching.

---

## Complete Flow

### 1. User PDF Upload
- **Endpoint**: `POST /api/upload`
- **File**: `app/api/routes.py`
- **Process**:
  - User uploads PDF file via API
  - File gets unique ID (UUID)
  - Background task starts processing
  - Returns upload_id for tracking

### 2. PDF Processing Pipeline
- **File**: `core/pipeline.py`
- **Steps**:
  1. Convert PDF to images (`utils/pdf_processor.py`)
  2. Extract text from images using OCR (`core/ocr_engine.py`)
  3. Clean extracted text (`utils/text_cleaner.py`)
  4. Process each page/document

### 3. Document Classification
- **File**: `core/document_classifier.py`
- **Logic**:
  - Analyzes extracted text
  - Matches against keyword lists
  - Determines document type:
    - **Payslip**: Contains keywords like "Gaji", "KWSP", "Cukai Pendapatan"
    - **Bank Statement**: Contains keywords like "Account", "Balance", "Transaction"
    - **Unknown**: No matching keywords found

### 4. Field Extraction
- **File**: `core/extractor.py`
- **Payslip Fields**:
  - Name (Nama)
  - ID Number (No K/P)
  - Gross Income (Gaji Pokok)
  - Net Income (Gaji Bersih)
  - Total Deduction (Jumlah Potongan)
  - Month/Year (Bulan)

- **Bank Statement Fields**:
  - Account Holder Name
  - Account Number
  - Statement Date

### 5. Data Validation
- **File**: `core/validators.py`
- **Process**:
  - Validates extracted data format
  - Calculates confidence score
  - Checks data completeness

### 6. Response Return
- **File**: `app/api/routes.py`
- **Endpoints**:
  - `GET /api/status/{upload_id}` - Check processing status
  - `GET /api/result/{upload_id}` - Get final extracted data
  - `GET /health` - Health check

---

## Features Implemented

### ✅ Completed Features
- PDF upload and processing
- Text extraction using Tesseract OCR
- Payslip classification and field extraction
- Bank Statement classification and field extraction
- Confidence scoring
- RESTful API endpoints
- Postman collection
- Logging system
- File management
- Text cleaning and normalization
- Data validation

### ❌ Not Implemented
- Database storage (results stored in memory only)
- Frontend UI (API-only)
- Batch processing (multiple files)
- Advanced validation rules
- Error handling improvements
- Rate limiting
- Authentication/Authorization
- Email notifications
- Export to Excel/CSV

---

## Technology Stack

- **Framework**: FastAPI
- **OCR Engine**: Tesseract
- **PDF Processing**: PyMuPDF
- **Server**: Uvicorn
- **Language**: Python 3.13
- **Data Validation**: Pydantic

---

## Setup & Running

### Prerequisites
```bash
pip install -r requirements-minimal.txt
pip install paddlepaddle
```

### Install Tesseract
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install to: `C:\Program Files\Tesseract-OCR`

### Start Server
```bash
python -m app.main
```

### Access API
- Swagger UI: `http://localhost:8003/docs`
- API Base: `http://localhost:8003/api`

### Import Postman Collection
1. Open Postman
2. Click "Import"
3. Select `postman_collection.json`
4. Use the collection to test endpoints

---

## Docker Deployment

### Windows Server Docker (PowerShell)

**Dockerfile for Windows Server:**
```dockerfile
FROM mcr.microsoft.com/windows/servercore:ltsc2022

# Install Python
RUN powershell -Command \
    Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe -OutFile python-installer.exe ; \
    .\python-installer.exe /quiet InstallAllUsers=1 PrependPath=1

# Install Tesseract
RUN powershell -Command \
    Invoke-WebRequest -Uri https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.0/tesseract-ocr-w64-setup-v5.3.0.exe -OutFile tesseract-installer.exe ; \
    .\tesseract-installer.exe /S

WORKDIR C:\app

COPY requirements-minimal.txt .

RUN pip install --no-cache-dir -r requirements-minimal.txt && \
    pip install --no-cache-dir paddlepaddle

COPY . .

EXPOSE 8003

CMD ["python", "-m", "app.main"]
```

**Build and Run:**
```powershell
# Build image
docker build -t document-extraction:latest .

# Run container
docker run -p 8003:8003 `
  -v C:\uploads:C:\app\uploads `
  -v C:\output:C:\app\output `
  document-extraction:latest
```

### Docker Compatibility Check

✅ **Fully Compatible Libraries:**
- fastapi, uvicorn, pydantic
- pymupdf, numpy, python-multipart
- python-dotenv, pyyaml, aiofiles

⚠️ **Requires System Dependencies:**
- paddleocr - Requires: libgomp1, libsm6, libxext6
- opencv-python - Requires: libsm6, libxext6, libxrender-dev

✅ **All libraries are Docker-compatible!**

---

## Performance Notes

- **Processing Time**: 30-60 seconds per PDF (depends on file size)
- **Memory Usage**: ~500MB for typical operations
- **Concurrent Requests**: Limited by CPU (single-threaded OCR)
- **File Size Limit**: 50MB per upload

---

## Future Enhancements

1. Database integration (PostgreSQL/MongoDB)
2. Web UI (React/Vue)
3. Batch processing API
4. Advanced ML-based classification
5. Multi-language support
6. Export functionality (Excel, CSV, JSON)
7. User authentication
8. Rate limiting & quotas
9. Webhook notifications
10. Performance optimization

---

