import logging
from typing import Dict, Any, List
from datetime import datetime
import json
from pathlib import Path

from core.ocr_engine import get_ocr_engine
from core.document_classifier import DocumentClassifier
from core.extractor import FieldExtractor
from core.validators import DataValidator
from utils.pdf_processor import PDFProcessor
from utils.text_cleaner import TextCleaner
from utils.file_manager import FileManager

logger = logging.getLogger(__name__)

class ExtractionPipeline:
    
    def __init__(self, ocr_engine: str = None):
        # Read OCR engine from config if not provided
        if ocr_engine is None:
            ocr_engine = self._load_ocr_engine_from_config()
        
        self.ocr_engine = get_ocr_engine(ocr_engine)
        self.classifier = DocumentClassifier()
        self.extractor = FieldExtractor()
        self.file_manager = FileManager()
        self.text_cleaner = TextCleaner()
    
    def _load_ocr_engine_from_config(self) -> str:
        """Load OCR engine name from config/ocr_config.json"""
        try:
            config_path = Path("config/ocr_config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    engine = config.get("engine", "paddleocr")
                    logger.info(f"Loaded OCR engine from config: {engine}")
                    return engine
            else:
                logger.warning("ocr_config.json not found, using default: paddleocr")
                return "paddleocr"
        except Exception as e:
            logger.error(f"Error loading OCR config: {str(e)}, using default: paddleocr")
            return "paddleocr"
    
    def process(self, upload_id: str, file_path: str) -> Dict[str, Any]:
        try:
            logger.info(f"Starting processing for {upload_id}")
            
            page_count = PDFProcessor.get_pdf_page_count(file_path)
            logger.info(f"PDF has {page_count} pages")
            
            images = PDFProcessor.pdf_to_images(
                file_path,
                self.file_manager.get_processed_dir(upload_id)
            )
            logger.info(f"Converted {len(images)} pages to images")
            
            documents = []
            total_text_length = 0
            confidence_scores = []
            
            for doc_num, image_path in enumerate(images, 1):
                logger.info(f"Processing page {doc_num}")
                
                text = self.ocr_engine.extract_text(image_path)
                text = self.text_cleaner.clean_text(text)
                total_text_length += len(text)
                
                # Log extracted text for debugging
                print(f"\n=== EXTRACTED TEXT (first 500 chars) ===\n{text[:500]}\n===")
                logger.info(f"Extracted text length: {len(text)}")
                
                # Save full text to file for debugging
                try:
                    debug_text_path = Path(self.file_manager.get_processed_dir(upload_id)) / f"extracted_text_page_{doc_num}.txt"
                    with open(debug_text_path, 'w', encoding='utf-8') as f:
                        f.write(text)
                    logger.info(f"Saved extracted text to {debug_text_path}")
                except Exception as e:
                    logger.warning(f"Could not save debug text: {str(e)}")
                
                doc_type, type_confidence = self.classifier.classify(text)
                logger.info(f"Classified as: {doc_type} (confidence: {type_confidence})")
                
                if doc_type == "payslip":
                    extracted_data = self.extractor.extract_payslip_fields(text)
                    is_valid, validation_msg = DataValidator.validate_payslip(extracted_data)
                elif doc_type == "bank_statement":
                    extracted_data = self.extractor.extract_bank_statement_fields(text)
                    is_valid, validation_msg = DataValidator.validate_bank_statement(extracted_data)
                else:
                    extracted_data = {}
                    is_valid = False
                    validation_msg = "Unknown document type"
                
                confidence = self.extractor.calculate_confidence(extracted_data)
                confidence_scores.append(confidence)
                
                logger.info(f"Extraction confidence: {confidence}")
                
                documents.append({
                    "document_number": doc_num,
                    "document_type": doc_type,
                    "extracted_data": extracted_data,
                    "confidence_score": confidence,
                    "text_length": len(text)
                })
            
            payslip_count = sum(1 for d in documents if d["document_type"] == "payslip")
            bank_count = sum(1 for d in documents if d["document_type"] == "bank_statement")
            other_count = len(documents) - payslip_count - bank_count
            
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            
            result = {
                "upload_id": upload_id,
                "file_type": "pdf",
                "total_documents": len(documents),
                "documents": documents,
                "summary": {
                    "payslips": payslip_count,
                    "bank_statements": bank_count,
                    "other": other_count,
                    "average_confidence": round(avg_confidence, 2)
                },
                "processing_completed_at": datetime.now().isoformat(),
                "original_file": f"raw/{upload_id}.pdf",
                "total_text_length": total_text_length
            }
            
            logger.info(f"Processing completed for {upload_id}")
            return result
        
        except Exception as e:
            logger.error(f"Processing error: {str(e)}")
            raise
    
    def save_result(self, upload_id: str, result: Dict[str, Any]):
        try:
            result_path = self.file_manager.get_result_path(upload_id)
            with open(result_path, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            logger.info(f"Result saved to {result_path}")
        except Exception as e:
            logger.error(f"Error saving result: {str(e)}")
            raise
