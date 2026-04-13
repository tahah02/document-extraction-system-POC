# API Documentation

**Version**: 1.0.0  
**Last Updated**: April 13, 2026

---

## Base URL

```
http://localhost:8000
```

---

## Endpoints

### 1. Upload Document

**Endpoint**: `POST /api/upload`

**Description**: Upload a PDF document for processing

**Request**:
```
Content-Type: multipart/form-data

Parameters:
- file (required): PDF file to upload
```

**Response** (200 OK):
```json
{
  "status": "processing",
  "upload_id": "f8fdcfa5-658a-40ef-8f8d-bc44d20a274d",
  "message": "File uploaded successfully. Processing started."
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@bank_statement.pdf"
```

---

### 2. Get Status

**Endpoint**: `GET /api/status/{upload_id}`

**Description**: Check processing status of uploaded document

**Response** (200 OK):
```json
{
  "status": "processing|completed|failed",
  "upload_id": "f8fdcfa5-658a-40ef-8f8d-bc44d20a274d",
  "message": "Processing in progress...",
  "detected_language": "en",
  "language_confidence": 0.95
}
```

**Example**:
```bash
curl "http://localhost:8000/api/status/f8fdcfa5-658a-40ef-8f8d-bc44d20a274d"
```

---

### 3. Get Results

**Endpoint**: `GET /api/result/{upload_id}`

**Description**: Retrieve extraction results for completed document

**Response** (200 OK):
```json
{
  "upload_id": "f8fdcfa5-658a-40ef-8f8d-bc44d20a274d",
  "file_type": "pdf",
  "total_documents": 1,
  "documents": [
    {
      "document_number": 1,
      "document_type": "bank_statement",
      "extracted_data": {
        "account_holder_name": "ENCIK MUHAMMAD SHAZWAN BIN SHARIFF",
        "account_number": "09010020435873",
        "statement_date": "31/07/25",
        "opening_balance": "142.52",
        "closing_balance": "122.60",
        "available_balance": null,
        "total_debit": "4340.78",
        "total_credit": "4320.86",
        "statement_period_from": "31/07/2025",
        "statement_period_to": "31/07/2025",
        "detected_bank": "bank_islam",
        "bank_detection_confidence": 1.0,
        "page_count": 4,
        "pages": [1, 2, 3, 4]
      },
      "confidence_score": 0.91,
      "text_length": 8520,
      "is_merged": true,
      "merged_from_pages": 4
    }
  ],
  "summary": {
    "payslips": 0,
    "bank_statements": 1,
    "other": 0,
    "average_confidence": 0.91
  },
  "processing_completed_at": "2026-04-13T14:41:27.098735",
  "original_file": "raw/f8fdcfa5-658a-40ef-8f8d-bc44d20a274d.pdf",
  "total_text_length": 8520,
  "config_version": "2.0.0",
  "template_used": "default"
}
```

**Example**:
```bash
curl "http://localhost:8000/api/result/f8fdcfa5-658a-40ef-8f8d-bc44d20a274d"
```

---

## Response Fields

### Bank Statement Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| account_holder_name | string | Account owner name | "ENCIK MUHAMMAD SHAZWAN BIN SHARIFF" |
| account_number | string | Bank account number | "09010020435873" |
| statement_date | string | Statement date (DD/MM/YYYY) | "31/07/25" |
| opening_balance | string | Opening balance (RM) | "142.52" |
| closing_balance | string | Closing balance (RM) | "122.60" |
| available_balance | string/null | Available balance (RM) | "110.16" |
| total_debit | string/null | Total debit (RM) | "4340.78" |
| total_credit | string/null | Total credit (RM) | "4320.86" |
| statement_period_from | string | Period start (DD/MM/YYYY) | "31/07/2025" |
| statement_period_to | string | Period end (DD/MM/YYYY) | "31/07/2025" |
| detected_bank | string | Bank type | "bank_islam" |
| bank_detection_confidence | float | Bank detection confidence (0-1) | 1.0 |
| page_count | integer | Number of pages | 4 |
| pages | array | Page numbers | [1, 2, 3, 4] |

### Document Summary

| Field | Type | Description |
|-------|------|-------------|
| payslips | integer | Number of payslips extracted |
| bank_statements | integer | Number of bank statements extracted |
| other | integer | Number of other documents |
| average_confidence | float | Average confidence score (0-1) |

---

## Supported Banks

### Bank Islam
- **Confidence**: 0.91
- **Features**: Multi-page merging, closing balance calculation
- **Debit/Credit**: Extracted from summary section
- **Format**: Account number (11 digits)

### CIMB
- **Confidence**: 0.82
- **Features**: Single/multi-page support
- **Debit/Credit**: N/A (format limitation)
- **Format**: Account number (11 digits with hyphens)

### BSN
- **Confidence**: 0.86
- **Features**: Available balance extraction
- **Debit/Credit**: Extracted from transactions
- **Format**: Account number (16 digits)

### Public Bank
- **Confidence**: 0.66
- **Features**: Multi-page support
- **Debit/Credit**: Extracted from transactions
- **Format**: Account number (10 digits)

---

## Error Responses

### 404 Not Found
```json
{
  "detail": "Upload ID not found"
}
```

### 202 Accepted (Still Processing)
```json
{
  "detail": "Processing not completed yet"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Processing failed: [error message]"
}
```

---

## Processing Flow

1. **Upload** → POST /api/upload
   - Returns upload_id
   - Processing starts in background

2. **Check Status** → GET /api/status/{upload_id}
   - Returns current status
   - Wait until status = "completed"

3. **Get Results** → GET /api/result/{upload_id}
   - Returns extracted data
   - Only available when status = "completed"

---

## Example Workflow

### Step 1: Upload Document
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@bank_statement.pdf"

# Response:
# {
#   "status": "processing",
#   "upload_id": "abc123",
#   "message": "File uploaded successfully. Processing started."
# }
```

### Step 2: Check Status (repeat until completed)
```bash
curl "http://localhost:8000/api/status/abc123"

# Response:
# {
#   "status": "processing",
#   "upload_id": "abc123",
#   "message": "Processing in progress..."
# }
```

### Step 3: Get Results
```bash
curl "http://localhost:8000/api/result/abc123"

# Response: Full extraction results
```

---

## Confidence Scores

- **0.90+**: Excellent - All fields extracted correctly
- **0.80-0.89**: Good - Most fields extracted correctly
- **0.70-0.79**: Fair - Some fields may need verification
- **0.60-0.69**: Poor - Multiple fields may be incorrect
- **<0.60**: Very Poor - Significant extraction errors

---

## Rate Limits

- No rate limiting implemented
- Concurrent requests: Limited by CPU
- File size limit: 50MB
- Processing timeout: 300 seconds

---

## Authentication

- No authentication required
- API is open for testing

---

## CORS

- CORS enabled for all origins
- Suitable for development/testing

---

## Swagger UI

Access interactive API documentation:
```
http://localhost:8000/docs
```

---

## Postman Collection

Import `postman_collection.json` for pre-configured requests

---

**Version**: 1.0.0  
**Last Updated**: April 13, 2026
