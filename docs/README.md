# Document Extraction System - Complete Solution

A FastAPI-based system for extracting structured data from PDF documents (Payslips and Bank Statements) using OCR and intelligent pattern matching.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements-minimal.txt
pip install paddlepaddle
```

### 2. Install Tesseract OCR
- Download: https://github.com/UB-Mannheim/tesseract/wiki
- Install to: `C:\Program Files\Tesseract-OCR`

### 3. Start Server
```bash
python -m app.main
```

### 4. Access API
- **Swagger UI**: http://localhost:8003/docs
- **API Base**: http://localhost:8003/api

---

## API Endpoints

### Upload Document
```
POST /api/upload
Content-Type: multipart/form-data

Body: file (PDF)

Response:
{
  "status": "processing",
  "upload_id": "uuid",
  "message": "File uploaded successfully. Processing started."
}
```

### Check Status
```
GET /api/status/{upload_id}

Response:
{
  "status": "completed",
  "upload_id": "uuid",
  "message": "Processing completed",
  "result": { ... }
}
```

### Get Results
```
GET /api/result/{upload_id}

Response:
{
  "upload_id": "uuid",
  "file_type": "pdf",
  "total_documents": 1,
  "documents": [
    {
      "document_number": 1,
      "document_type": "payslip",
      "extracted_data": {
        "name": "...",
        "id_number": "...",
        "gross_income": "...",
        "net_income": "...",
        "total_deduction": "...",
        "month_year": "..."
      },
      "confidence_score": 0.95,
      "text_length": 698
    }
  ],
  "summary": {
    "payslips": 1,
    "bank_statements": 0,
    "other": 0,
    "average_confidence": 0.95
  },
  "processing_completed_at": "2026-04-05T...",
  "original_file": "raw/uuid.pdf",
  "total_text_length": 698
}
```

---

## Supported Document Types

### Payslip
Extracts:
- Employee Name
- ID Number (NRIC)
- Gross Income
- Net Income
- Total Deductions
- Pay Period (Month/Year)

### Bank Statement
Extracts:
- Account Holder Name
- Account Number
- Statement Date

---

## Project Structure

```
document-extraction-poc/
├── app/
│   ├── api/
│   │   ├── routes.py          # API endpoints
│   │   └── schemas.py         # Response models
│   ├── main.py                # Server startup
│   └── config.py              # Configuration
├── core/
│   ├── pipeline.py            # Processing pipeline
│   ├── ocr_engine.py          # OCR integration
│   ├── document_classifier.py # Document classification
│   ├── extractor.py           # Field extraction
│   └── validators.py          # Data validation
├── utils/
│   ├── pdf_processor.py       # PDF to image conversion
│   ├── text_cleaner.py        # Text cleaning
│   ├── file_manager.py        # File management
│   └── logger.py              # Logging
├── models/
│   ├── payslip.py
│   ├── bank_statement.py
│   └── extraction_result.py
├── config/
│   ├── app_config.yaml
│   ├── extraction_config.json
│   └── ocr_config.json
├── uploads/                   # Uploaded files
├── output/                    # Processing results
├── requirements-minimal.txt   # Dependencies
├── postman_collection.json    # Postman API collection
└── project-solution/          # Documentation
    ├── PROJECT_FLOW.md
    └── README.md
```

---

## Testing with Postman

1. Open Postman
2. Click "Import"
3. Select `postman_collection.json`
4. Use the collection to test endpoints

**Endpoints in Collection:**
- Upload Document
- Get Status
- Get Result
- Health Check

---

## Docker Deployment (Windows Server)

### Build Image
```powershell
docker build -t document-extraction:latest .
```

### Run Container
```powershell
docker run -p 8003:8003 `
  -v C:\uploads:C:\app\uploads `
  -v C:\output:C:\app\output `
  document-extraction:latest
```

### Docker Compatibility
✅ All libraries are Docker-compatible
- FastAPI, Uvicorn, Pydantic
- PyMuPDF, NumPy, OpenCV
- PaddleOCR, Tesseract

---

## Response Tags Reference

### Top-Level Tags
| Tag | Type | Description |
|-----|------|-------------|
| `status` | string | processing/completed/failed |
| `upload_id` | string | Unique file identifier |
| `message` | string | Status message |
| `result` | object | Extraction result |

### Payslip Fields
| Tag | Type | Description |
|-----|------|-------------|
| `name` | string | Employee name |
| `id_number` | string | NRIC/ID number |
| `gross_income` | string | Gross salary |
| `net_income` | string | Net salary |
| `total_deduction` | string | Total deductions |
| `month_year` | string | Pay period |

### Bank Statement Fields
| Tag | Type | Description |
|-----|------|-------------|
| `account_holder_name` | string | Account owner |
| `account_number` | string | Account number |
| `statement_date` | string | Statement date |

### Summary Tags
| Tag | Type | Description |
|-----|------|-------------|
| `payslips` | integer | Payslip count |
| `bank_statements` | integer | Bank statement count |
| `other` | integer | Unknown document count |
| `average_confidence` | float | Overall confidence |

---

## Features

✅ **Implemented**
- PDF upload and processing
- Text extraction (Tesseract OCR)
- Payslip classification & extraction
- Bank Statement classification & extraction
- Confidence scoring
- RESTful API
- Postman collection
- Logging system
- File management

❌ **Not Implemented**
- Database storage
- Frontend UI
- Batch processing
- Authentication
- Rate limiting

---

## Performance

- **Processing Time**: 30-60 seconds per PDF
- **Memory Usage**: ~500MB
- **File Size Limit**: 50MB
- **Concurrent Requests**: Limited by CPU

---

## Troubleshooting

### Tesseract not found
Install from: https://github.com/UB-Mannheim/tesseract/wiki

### oneDNN error
Environment variables already set in `app/main.py`

### Processing timeout
Increase timeout in `core/pipeline.py`

### Low confidence scores
Improve extraction patterns in `core/extractor.py`

---

## Technology Stack

- **Framework**: FastAPI
- **OCR**: Tesseract
- **PDF**: PyMuPDF
- **Server**: Uvicorn
- **Language**: Python 3.13
- **Validation**: Pydantic

---

## License
Educational purposes only

---

**Version**: 0.1.0  
**Last Updated**: April 6, 2026
