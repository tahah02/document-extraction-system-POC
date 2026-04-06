# API Documentation

## Base URL

```
http://localhost:8000/api
```

## Endpoints

### 1. Health Check

**GET** `/health`

Check if the service is running.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

---

### 2. Upload Document

**POST** `/upload`

Upload a document for extraction.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (PDF, JPG, PNG, DOCX)

**Response:**
```json
{
  "status": "processing",
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "File uploaded successfully. Processing started."
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@payslip.pdf"
```

---

### 3. Check Processing Status

**GET** `/status/{upload_id}`

Check the status of document processing.

**Parameters:**
- `upload_id` (path): ID returned from upload endpoint

**Response (Processing):**
```json
{
  "status": "processing",
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Analyzing document..."
}
```

**Response (Completed):**
```json
{
  "status": "completed",
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "result": {
    "upload_id": "550e8400-e29b-41d4-a716-446655440000",
    "file_type": "pdf",
    "total_documents": 1,
    "documents": [
      {
        "document_number": 1,
        "document_type": "payslip",
        "extracted_data": {
          "name": "SITI HAZIRAH BT MUSTAFA",
          "id_number": "800408-06-5592",
          "gross_income": "15898.00",
          "net_income": "9888.20",
          "total_deduction": "6009.80",
          "month_year": "02/2026"
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
    "processing_completed_at": "2026-04-03T08:19:07.168115",
    "original_file": "raw/550e8400-e29b-41d4-a716-446655440000.pdf",
    "total_text_length": 920
  }
}
```

**Example:**
```bash
curl "http://localhost:8000/api/status/550e8400-e29b-41d4-a716-446655440000"
```

---

### 4. Get Extraction Results

**GET** `/result/{upload_id}`

Retrieve the complete extraction results.

**Parameters:**
- `upload_id` (path): ID returned from upload endpoint

**Response:**
```json
{
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "file_type": "pdf",
  "total_documents": 1,
  "documents": [
    {
      "document_number": 1,
      "document_type": "payslip",
      "extracted_data": {
        "name": "SITI HAZIRAH BT MUSTAFA",
        "id_number": "800408-06-5592",
        "gross_income": "15898.00",
        "net_income": "9888.20",
        "total_deduction": "6009.80",
        "month_year": "02/2026"
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
  "processing_completed_at": "2026-04-03T08:19:07.168115",
  "original_file": "raw/550e8400-e29b-41d4-a716-446655440000.pdf",
  "total_text_length": 920
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "status": "error",
  "error": "No file provided",
  "details": null
}
```

### 404 Not Found
```json
{
  "status": "error",
  "error": "Upload ID not found",
  "details": null
}
```

### 500 Internal Server Error
```json
{
  "status": "error",
  "error": "Processing failed",
  "details": "Error message details"
}
```

---

## Workflow Example

```bash
# 1. Upload document
UPLOAD_ID=$(curl -s -X POST "http://localhost:8000/api/upload" \
  -F "file=@payslip.pdf" | jq -r '.upload_id')

echo "Upload ID: $UPLOAD_ID"

# 2. Check status (repeat until completed)
curl "http://localhost:8000/api/status/$UPLOAD_ID"

# 3. Get results when completed
curl "http://localhost:8000/api/result/$UPLOAD_ID"
```

---

## Rate Limiting

Currently no rate limiting. Implement as needed for production.

## Authentication

Currently no authentication. Implement as needed for production.

## CORS

CORS is enabled for all origins by default. Configure in `.env` for production.
