# System Architecture

## Overview

The Document Extraction System is built with a modular architecture designed for scalability and maintainability.

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              API Routes (app/api/)                   │   │
│  │  - Upload endpoint                                   │   │
│  │  - Status check endpoint                             │   │
│  │  - Result retrieval endpoint                         │   │
│  └──────────────────────────────────────────────────────┘   │
│                           ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Core Processing Pipeline (core/)             │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │ 1. PDF Processor (pdf_processor.py)            │  │   │
│  │  │    - Convert PDF to images                     │  │   │
│  │  │    - Handle multi-page documents               │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │                      ↓                                │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │ 2. OCR Engine (ocr_engine.py)                  │  │   │
│  │  │    - PaddleOCR / EasyOCR / Tesseract           │  │   │
│  │  │    - Extract text with coordinates             │  │   │
│  │  │    - CPU-optimized processing                  │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │                      ↓                                │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │ 3. Document Classifier (document_classifier.py)│  │   │
│  │  │    - Detect document type                      │  │   │
│  │  │    - Payslip vs Bank Statement                 │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │                      ↓                                │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │ 4. Text Cleaner (text_cleaner.py)              │  │   │
│  │  │    - Normalize text                            │  │   │
│  │  │    - Clean special characters                  │  │   │
│  │  │    - Format standardization                    │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │                      ↓                                │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │ 5. Field Extractor (extractor.py)              │  │   │
│  │  │    - Extract specific fields                   │  │   │
│  │  │    - Keyword-based matching                    │  │   │
│  │  │    - Pattern recognition                       │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │                      ↓                                │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │ 6. Data Validator (validators.py)              │  │   │
│  │  │    - Validate extracted data                   │  │   │
│  │  │    - Format verification                       │  │   │
│  │  │    - Confidence scoring                        │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
│                           ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Output & Storage                           │   │
│  │  - JSON results (output/json/)                       │   │
│  │  - Processing logs (output/logs/)                    │   │
│  │  - Temporary files (temp/)                           │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. API Layer (`app/api/`)
- **routes.py**: Defines HTTP endpoints
- **schemas.py**: Pydantic models for request/response validation
- **config.py**: Application configuration management

### 2. Core Processing (`core/`)
- **ocr_engine.py**: Abstract OCR interface with multiple implementations
- **document_classifier.py**: Identifies document type
- **extractor.py**: Extracts fields using configuration
- **validators.py**: Validates extracted data

### 3. Utilities (`utils/`)
- **pdf_processor.py**: PDF to image conversion
- **text_cleaner.py**: Text preprocessing
- **logger.py**: Logging configuration
- **helpers.py**: General utility functions

### 4. Data Models (`models/`)
- **payslip.py**: Payslip data structure
- **bank_statement.py**: Bank statement data structure
- **extraction_result.py**: Complete result structure

### 5. Configuration (`config/`)
- **extraction_config.json**: Field mapping and keywords
- **ocr_config.json**: OCR engine settings
- **app_config.yaml**: Application settings

## Data Flow

```
User Upload
    ↓
[API: /upload]
    ↓
[PDF Processor] → Convert to images
    ↓
[OCR Engine] → Extract text
    ↓
[Document Classifier] → Identify type
    ↓
[Text Cleaner] → Normalize text
    ↓
[Field Extractor] → Extract fields
    ↓
[Data Validator] → Validate & score
    ↓
[JSON Output] → Store results
    ↓
User Retrieval [API: /result/{id}]
```

## Processing Modes

### Synchronous (Current)
- Simple implementation
- Good for small documents
- Blocking API calls

### Asynchronous (Recommended for Production)
- Background task processing
- Non-blocking API calls
- Queue-based system (Celery, RQ)

## Scalability Considerations

### Horizontal Scaling
- Stateless API design
- Distributed task queue
- Shared result storage (Database)

### Vertical Scaling
- Multi-worker configuration
- Async processing
- Caching mechanisms

### Performance Optimization
- Image preprocessing
- OCR model caching
- Result caching
- Batch processing

## Security Considerations

1. **File Upload**
   - Validate file types
   - Limit file size
   - Scan for malware

2. **Data Privacy**
   - Encrypt sensitive data
   - Secure temporary storage
   - Audit logging

3. **API Security**
   - Authentication/Authorization
   - Rate limiting
   - Input validation

## Error Handling

```
Processing Error
    ↓
[Log Error]
    ↓
[Update Status: Failed]
    ↓
[Return Error Response]
    ↓
[Cleanup Resources]
```

## Monitoring & Logging

- Application logs: `output/logs/app.log`
- Processing metrics: Document count, confidence scores
- Performance metrics: Processing time, memory usage
- Error tracking: Failed extractions, validation errors

## Future Enhancements

1. Database integration for result storage
2. Distributed task queue (Celery)
3. Advanced ML models for field extraction
4. Multi-language support
5. Real-time processing dashboard
6. API authentication & authorization
7. Advanced caching strategies
8. Webhook notifications
