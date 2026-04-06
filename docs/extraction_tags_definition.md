# Document Extraction Tags Definition

## Overview
This document defines all the tags/fields that should be extracted from Pay Slips and Bank Statements.

---

## PAYSLIP EXTRACTION TAGS

### Basic Information
- **name**: Full name of the employee
  - Example: "SITI HAZIRAH BT MUSTAFA"
  - Type: String

- **id_number**: National ID or Employee ID number
  - Example: "800408-06-5592"
  - Type: String (format: XXXXXX-XX-XXXX for Malaysian ID)

### Income Information
- **gross_income**: Total income before deductions
  - Example: "15898.00" or "15,898.00"
  - Type: Decimal/Float
  - Note: May contain comma separators

- **net_income**: Take-home income after all deductions
  - Example: "9888.20" or "9,888.20"
  - Type: Decimal/Float
  - Note: May contain comma separators

- **total_deduction**: Total amount deducted from gross income
  - Example: "6009.80" or "6,009.80"
  - Type: Decimal/Float
  - Note: May contain comma separators

### Period Information
- **month_year**: Pay period (month and year)
  - Example: "02/2026" or "11/2025"
  - Type: String (format: MM/YYYY)

---

## BANK STATEMENT EXTRACTION TAGS

### Account Information
- **account_holder_name**: Name of the account holder
  - Example: "SITI AISAH BINTI GHAZALI"
  - Type: String

- **account_number**: Bank account number
  - Example: "51-1103355-2"
  - Type: String (format may vary by bank)

### Statement Information
- **statement_date**: Date of the bank statement
  - Example: "28/02/2026"
  - Type: String (format: DD/MM/YYYY)

---

## METADATA FIELDS (System Generated)

- **document_type**: Type of document
  - Values: "payslip" or "bank_statement"
  - Type: String

- **confidence_score**: Confidence level of extraction accuracy
  - Example: 0.95
  - Type: Float (0.0 to 1.0)
  - Target: >= 0.95 (95%)

- **text_length**: Total character count of extracted text
  - Example: 916
  - Type: Integer

---

## JSON OUTPUT STRUCTURE

```json
{
  "status": "completed",
  "upload_id": "unique-id",
  "result": {
    "upload_id": "unique-id",
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
    "original_file": "raw/file-id.pdf",
    "total_text_length": 920
  },
  "retrieved_at": "2026-04-03T08:19:09.989818"
}
```

---

## EXTRACTION REQUIREMENTS

1. **Accuracy Target**: 95% confidence score minimum
2. **Format Consistency**: 
   - Numbers should be normalized (remove commas for processing)
   - Dates should follow MM/YYYY for payslips, DD/MM/YYYY for bank statements
3. **Handling Missing Fields**: If a field cannot be extracted, mark as null or empty string
4. **Multi-Document Support**: System should handle PDFs with multiple documents
5. **Document Classification**: Automatically detect and classify as payslip or bank_statement

