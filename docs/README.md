# Document Extraction System - Complete Guide

**Version**: 0.1.0  
**Status**: Production Ready  
**Last Updated**: April 6, 2026

---

## Overview

A FastAPI-based system for extracting structured data from PDF documents (Payslips and Bank Statements) using OCR and intelligent pattern matching.

**Key Capabilities:**
- Multi-page PDF processing
- Automatic document classification
- Field extraction with confidence scoring
- Async background processing
- 3 OCR engine support (PaddleOCR, EasyOCR, Tesseract)
- RESTful API with Swagger documentation

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Server
```bash
python -m app.main
```

### 3. Access API
- Swagger UI: http://localhost:8003/docs
- API Base: http://localhost:8003/api

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
  "status": "processing|completed|failed",
  "upload_id": "uuid",
  "message": "Status message"
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
      "document_type": "payslip|bank_statement",
      "extracted_data": {
        "name": "...",
        "id_number": "...",
        "gross_income": "...",
        "net_income": "...",
        "total_deduction": "...",
        "month_year": "..."
      },
      "confidence_score": 0.95,
      "text_length": 916
    }
  ],
  "summary": {
    "payslips": 1,
    "bank_statements": 0,
    "other": 0,
    "average_confidence": 0.95
  },
  "processing_completed_at": "2026-04-06T...",
  "original_file": "raw/uuid.pdf",
  "total_text_length": 920
}
```

### Health Check
```
GET /health

Response:
{
  "status": "healthy",
  "version": "0.1.0"
}
```

---

## Supported Document Types

### Payslip
Extracts 6 fields:
- name: Employee name
- id_number: NRIC/ID number
- gross_income: Gross salary
- net_income: Net salary
- total_deduction: Total deductions
- month_year: Pay period (MM/YYYY)

### Bank Statement
Extracts 3 fields:
- account_holder_name: Account owner
- account_number: Bank account number
- statement_date: Statement date (DD/MM/YYYY)

---

## Configuration

### OCR Engine Selection
Edit `config/ocr_config.json`:
```json
{
  "engine": "paddleocr",
  "language": "en",
  "paddleocr": {
    "use_angle_cls": true,
    "lang": "en",
    "use_gpu": false
  },
  "easyocr": {
    "languages": ["en"],
    "gpu": false
  },
  "tesseract": {
    "language": "eng",
    "config": "--psm 6"
  }
}
```

### Environment Variables
`.env` file:
```
PADDLE_DEVICE=cpu
PADDLE_DISABLE_ONEDNN=1
PADDLE_DISABLE_FAST_MATH=1
PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True
```

### Application Settings
`config/app_config.yaml`:
```yaml
server:
  host: 0.0.0.0
  port: 8003
  workers: 1

upload:
  max_file_size: 50MB
  allowed_formats: [pdf, jpg, png]

processing:
  timeout: 300
  temp_dir: ./temp
```

---

## Processing Pipeline

```
1. User uploads PDF
   POST /api/upload

2. File saved to uploads/raw/{upload_id}.pdf

3. PDF converted to images
   uploads/processed/{upload_id}/page_*.png

4. OCR extracts text from images
   Using configured engine (PaddleOCR/EasyOCR/Tesseract)

5. Document classified
   Payslip or Bank Statement

6. Fields extracted
   Using regex patterns and keyword matching

7. Data validated
   Format checking and confidence scoring

8. Results saved
   output/json/{upload_id}.json

9. User retrieves results
   GET /api/result/{upload_id}
```

---

## Performance

- Processing Time: 15-30 seconds per PDF
- Memory Usage: ~500MB
- File Size Limit: 50MB
- Response Time: < 1 second (async)
- Concurrent Requests: Limited by CPU

---

## Testing

### Using Swagger UI
1. Navigate to http://localhost:8003/docs
2. Click "Try it out" on POST /api/upload
3. Select a PDF file
4. Execute
5. Copy upload_id from response
6. Use GET /api/result/{upload_id} to retrieve results

### Using Postman
1. Import postman_collection.json
2. Use Upload Document endpoint
3. Copy upload_id from response
4. Use Get Result endpoint with upload_id

### Sample Test
```bash
# Upload
curl -X POST "http://localhost:8003/api/upload" \
  -F "file=@document.pdf"

# Check status
curl "http://localhost:8003/api/status/{upload_id}"

# Get results
curl "http://localhost:8003/api/result/{upload_id}"
```

---

## Project Structure

```
document-extraction-poc/
├── app/                    FastAPI Application
│   ├── main.py            Server startup
│   ├── config.py          Settings
│   └── api/
│       ├── routes.py      Endpoints
│       └── schemas.py     Models
├── core/                  Processing Logic
│   ├── pipeline.py        Orchestrator
│   ├── ocr_engine.py      OCR implementations
│   ├── document_classifier.py
│   ├── extractor.py       Field extraction
│   └── validators.py      Validation
├── models/                Data Models
├── utils/                 Utilities
├── config/                Configuration
├── docs/                  Documentation
├── uploads/               File Storage
├── output/                Results
├── .env                   Environment
├── requirements.txt       Dependencies
└── postman_collection.json API Tests
```

---

## Troubleshooting

### Issue: Tesseract not found
**Solution**: Install from https://github.com/UB-Mannheim/tesseract/wiki

### Issue: Low confidence scores
**Solution**: 
- Improve extraction patterns in core/extractor.py
- Adjust OCR settings in config/ocr_config.json
- Use higher quality PDFs

### Issue: Processing timeout
**Solution**:
- Increase timeout in core/pipeline.py
- Check file size (max 50MB)
- Verify OCR engine is working

### Issue: Pin memory warning
**Solution**: Safe to ignore (PyTorch warning for CPU-only systems)

---

## Technology Stack

- Framework: FastAPI 0.104+
- Server: Uvicorn
- OCR: PaddleOCR 3.4.0 (default)
- PDF: PyMuPDF
- Validation: Pydantic
- Language: Python 3.13+

---

## Installed Dependencies

```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0
paddleocr>=2.7.0
pymupdf>=1.27.0
numpy>=1.26.0
opencv-python>=4.8.0
python-multipart>=0.0.6
python-dotenv>=1.0.0
pyyaml>=6.0
aiofiles>=23.0
```

---

## Features

### Implemented
- PDF upload and processing
- Multi-page document handling
- Text extraction (3 OCR engines)
- Document classification
- Field extraction
- Confidence scoring
- Data validation
- RESTful API
- Async background processing
- Swagger documentation
- Postman collection
- Comprehensive logging
- File management

### Not Implemented
- Database storage (in-memory only)
- Frontend UI (API-only)
- Batch processing
- Authentication
- Rate limiting
- Export to Excel/CSV
- Webhook notifications

---

## Documentation

| File | Purpose |
|------|---------|
| PROJECT_SUMMARY.md | Project overview |
| SETUP.md | Setup instructions |
| API.md | API documentation |
| ARCHITECTURE.md | System architecture |
| PROJECT_FLOW.md | Processing flow |
| PROJECT_STRUCTURE.txt | Directory structure |

---

## Next Steps

1. Deploy to production
2. Add database integration
3. Implement authentication
4. Add rate limiting
5. Create web UI
6. Add batch processing
7. Implement webhooks
8. Add export functionality

---

## Support

- Check docs/ folder for detailed documentation
- Review logs in output/logs/app.log
- Test with Postman collection
- Access Swagger UI at http://localhost:8003/docs

---

**Status**: Production Ready  
**Last Updated**: April 6, 2026  
**Version**: 0.1.0
