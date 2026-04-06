from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime

class DocumentExtraction(BaseModel):
    document_number: int
    document_type: str
    extracted_data: Dict[str, Any]
    confidence_score: float
    text_length: int

class ExtractionSummary(BaseModel):
    payslips: int
    bank_statements: int
    other: int
    average_confidence: float

class ExtractionResult(BaseModel):
    upload_id: str
    file_type: str
    total_documents: int
    documents: List[DocumentExtraction]
    summary: ExtractionSummary
    processing_completed_at: datetime
    original_file: str
    total_text_length: int
