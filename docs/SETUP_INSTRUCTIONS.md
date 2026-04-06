# Document Extraction POC - Complete Setup

## ✅ Project Structure Created

Your complete project structure has been created in the `document-extraction-poc/` folder with all necessary files and directories.

### Directory Tree

```
document-extraction-poc/
├── app/                          # FastAPI Application
│   ├── __init__.py
│   ├── main.py                   # Entry point
│   ├── config.py                 # Configuration
│   └── api/
│       ├── __init__.py
│       ├── routes.py             # API endpoints
│       └── schemas.py            # Pydantic models
│
├── core/                         # Core Processing Logic
│   ├── __init__.py
│   ├── ocr_engine.py             # OCR implementations
│   ├── document_classifier.py    # Document type detection
│   ├── extractor.py              # Field extraction
│   └── validators.py             # Data validation
│
├── models/                       # Data Models
│   ├── __init__.py
│   ├── payslip.py
│   ├── bank_statement.py
│   └── extraction_result.py
│
├── utils/                        # Utility Functions
│   ├── __init__.py
│   ├── pdf_processor.py          # PDF to image conversion
│   ├── text_cleaner.py           # Text preprocessing
│   ├── logger.py                 # Logging
│   └── helpers.py                # Helper functions
│
├── config/                       # Configuration Files
│   ├── extraction_config.json    # Field mapping
│   ├── ocr_config.json           # OCR settings
│   └── app_config.yaml           # App settings
│
├── tests/                        # Test Suite
│   ├── __init__.py
│   └── test_extractor.py
│
├── docs/                         # Documentation
│   ├── SETUP.md                  # Setup guide
│   ├── API.md                    # API documentation
│   └── ARCHITECTURE.md           # Architecture
│
├── README.md                     # Project overview
├── requirements.txt              # Dependencies
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore
└── PROJECT_STRUCTURE.txt         # Structure reference
```

---

## 🚀 Quick Start

### Step 1: Navigate to Project
```bash
cd document-extraction-poc
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Setup Environment
```bash
# Copy example env file
cp .env.example .env

# Edit .env if needed (optional for basic setup)
```

### Step 5: Create Required Directories
```bash
mkdir -p uploads/raw uploads/processed
mkdir -p output/json output/logs
mkdir -p temp
```

### Step 6: Run Application
```bash
python -m app.main
```

The API will be available at: **http://localhost:8000**

---

## 📚 Documentation

### Available Docs
- **SETUP.md** - Detailed setup and installation guide
- **API.md** - Complete API documentation with examples
- **ARCHITECTURE.md** - System architecture and data flow

### Access API Documentation
Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔧 Configuration

### OCR Engine Selection

**Option 1: PaddleOCR (Recommended for CPU)**
```bash
pip install paddleocr
# Edit config/ocr_config.json: "engine": "paddleocr"
```

**Option 2: EasyOCR**
```bash
pip install easyocr
# Edit config/ocr_config.json: "engine": "easyocr"
```

**Option 3: Tesseract**
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows - Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Edit config/ocr_config.json: "engine": "tesseract"
```

### Customize Extraction Fields

Edit `config/extraction_config.json` to add/modify field keywords and patterns for your specific documents.

---

## 📋 Extracted Fields

### Payslip Fields
- `name` - Employee name
- `id_number` - National ID (format: XXXXXX-XX-XXXX)
- `gross_income` - Total income before deductions
- `net_income` - Take-home income
- `total_deduction` - Total deductions
- `month_year` - Pay period (MM/YYYY)

### Bank Statement Fields
- `account_holder_name` - Account owner name
- `account_number` - Bank account number (format: XX-XXXXXXX-X)
- `statement_date` - Statement date (DD/MM/YYYY)

---

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=core tests/
```

---

## 📤 API Usage Example

### Upload Document
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@payslip.pdf"
```

Response:
```json
{
  "status": "processing",
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "File uploaded successfully. Processing started."
}
```

### Check Status
```bash
curl "http://localhost:8000/api/status/550e8400-e29b-41d4-a716-446655440000"
```

### Get Results
```bash
curl "http://localhost:8000/api/result/550e8400-e29b-41d4-a716-446655440000"
```

---

## 🐛 Troubleshooting

### PaddleOCR Download Issues
- First run downloads models (~200MB)
- Set: `PADDLEOCR_HOME=/path/to/cache`

### Memory Issues
- Reduce image zoom in `config/ocr_config.json`
- Process one document at a time

### Slow Processing
- Use Tesseract for faster (less accurate) results
- Reduce image DPI in configuration

---

## 📦 Project Components

### Core Modules

**app/main.py**
- FastAPI application setup
- Route registration
- CORS configuration

**core/ocr_engine.py**
- Abstract OCR interface
- PaddleOCR implementation
- EasyOCR implementation
- Tesseract implementation

**core/document_classifier.py**
- Automatic document type detection
- Keyword-based classification

**core/extractor.py**
- Field extraction logic
- Configuration-based extraction
- Pattern matching

**core/validators.py**
- Data validation
- Format verification
- Confidence scoring

**utils/pdf_processor.py**
- PDF to image conversion
- Multi-page handling

**utils/text_cleaner.py**
- Text normalization
- Currency formatting
- Date formatting

---

## 🔐 Security Notes

For production deployment:
1. Add authentication/authorization
2. Implement rate limiting
3. Validate file uploads
4. Encrypt sensitive data
5. Use HTTPS
6. Set up proper logging
7. Implement monitoring

---

## 📊 Performance Tips

1. **CPU Optimization**
   - Use Tesseract for speed
   - Reduce image resolution
   - Batch process documents

2. **Memory Optimization**
   - Process one page at a time
   - Clean up temporary files
   - Use streaming for large files

3. **Accuracy Optimization**
   - Use PaddleOCR for better accuracy
   - Increase image DPI
   - Customize extraction patterns

---

## 🎯 Next Steps

1. ✅ Project structure created
2. ⏭️ Install dependencies
3. ⏭️ Configure OCR engine
4. ⏭️ Test with sample documents
5. ⏭️ Customize extraction config
6. ⏭️ Deploy to production

---

## 📞 Support

For issues or questions:
1. Check `docs/SETUP.md` for detailed setup
2. Review `docs/API.md` for API usage
3. Check `docs/ARCHITECTURE.md` for system design
4. Review logs in `output/logs/app.log`

---

## 📝 Notes

- All configuration files are in JSON/YAML format
- Extraction patterns can be customized per document type
- System supports multi-page PDF documents
- Results are saved as JSON for easy integration
- Logging is configured for debugging

---

**Happy extracting! 🎉**
