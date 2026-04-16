import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.ocr_engine import get_ocr_engine
from core.document_classifier import DocumentClassifier
from core.extractor import FieldExtractor
from core.validators import DataValidator
from core.config import get_config
from core.statement_merger import StatementMerger
from core.pdfplumber_engine import PDFPlumberEngine
from utils.pdf_processor import PDFProcessor
from utils.text_cleaner import TextCleaner
from utils.file_manager import FileManager


try:
    from core.image_preprocessor import ImagePreprocessor
    from core.ensemble_ocr import EnsembleOCR
    PREPROCESSING_AVAILABLE = True
except ImportError:
    PREPROCESSING_AVAILABLE = False
    logging.warning("Preprocessing modules not available, using legacy OCR")

logger = logging.getLogger(__name__)

class ExtractionPipeline:
    
    def __init__(self, ocr_engine: str = None, template: str = None):
        if ocr_engine is None:
            ocr_engine = self._load_ocr_engine_from_config()
        
        self.template = template
        self.file_manager = FileManager()
        self.text_cleaner = TextCleaner()
        self.classifier = DocumentClassifier()
        self.extractor = FieldExtractor(template=template)
        self.pdfplumber_engine = PDFPlumberEngine()
        
        self.use_preprocessing = PREPROCESSING_AVAILABLE
        if self.use_preprocessing:
            try:
                preprocessing_config_path = Path("config/preprocessing_config.json")
                if preprocessing_config_path.exists():
                    with open(preprocessing_config_path, 'r') as f:
                        self.preprocessing_config = json.load(f)
                    
                    self.preprocessor = ImagePreprocessor(self.preprocessing_config, template=template)
                    self.ensemble_ocr = EnsembleOCR(self.preprocessing_config)
                    logger.info("Using NEW preprocessing + ensemble OCR pipeline")
                else:
                    logger.warning("preprocessing_config.json not found, using legacy OCR")
                    self.use_preprocessing = False
                    self.ocr_engine = get_ocr_engine(ocr_engine)
            except Exception as e:
                logger.error(f"Failed to initialize preprocessing: {str(e)}, using legacy OCR")
                self.use_preprocessing = False
                self.ocr_engine = get_ocr_engine(ocr_engine)
        else:
            self.ocr_engine = get_ocr_engine(ocr_engine)
        
        config = get_config(template)
        config_version = config.get("config_version", "unknown")
        logger.info(f"Pipeline initialized with config version: {config_version}, template: {template or 'default'}, preprocessing: {self.use_preprocessing}")
    
    def _load_ocr_engine_from_config(self) -> str:
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
    
    def _process_single_page(self, doc_num: int, image_path: str, upload_id: str) -> Dict[str, Any]:
        logger.info(f"Processing page {doc_num}")
        
        if self.use_preprocessing:
            preprocessed_path, preprocess_metadata = self.preprocessor.preprocess(
                image_path, 
                save_debug=True, 
                upload_id=upload_id
            )
            logger.info(f"Preprocessing applied: {preprocess_metadata.get('steps_applied', [])}")
            
            text, tokens = self.ensemble_ocr.extract_text_with_tokens(
                preprocessed_path,
                page=doc_num-1,
                save_debug=True,
                upload_id=upload_id
            )
            logger.info(f"Extracted {len(tokens)} tokens using ensemble OCR")
        else:
            tokens = self.ocr_engine.extract_tokens(image_path, page=doc_num-1)
            logger.info(f"Extracted {len(tokens)} tokens from page {doc_num}")
            text = self.ocr_engine.extract_text(image_path)
        
        text = self.text_cleaner.clean_text(text)
        
        print(f"\n=== EXTRACTED TEXT (first 500 chars) ===\n{text[:500]}\n===")
        logger.info(f"Extracted text length: {len(text)}")
        
        try:
            debug_text_path = Path(self.file_manager.get_processed_dir(upload_id)) / f"extracted_text_page_{doc_num}.txt"
            with open(debug_text_path, 'w', encoding='utf-8') as f:
                f.write(text)
            logger.info(f"Saved extracted text to {debug_text_path}")
        except Exception as e:
            logger.warning(f"Could not save debug text: {str(e)}")
        
        doc_type, type_confidence = self.classifier.classify(text, self.template)
        logger.info(f"Classified as: {doc_type} (confidence: {type_confidence})")
        
        extracted_data = self.extractor.extract_bank_statement_fields(text, tokens=tokens)
        is_valid, validation_msg = DataValidator.validate_bank_statement(extracted_data, self.template)
        
        confidence = self.extractor.calculate_confidence(extracted_data)
        logger.info(f"Extraction confidence: {confidence}")
        
        return {
            "document_number": doc_num,
            "document_type": doc_type,
            "extracted_data": extracted_data,
            "confidence_score": confidence,
            "text_length": len(text)
        }
    
    def process(self, upload_id: str, file_path: str) -> Dict[str, Any]:
        try:
            logger.info(f"Starting processing for {upload_id}")
            
            use_pdfplumber = self.pdfplumber_engine.can_extract_text(file_path)
            
            if use_pdfplumber:
                logger.info("Digital PDF detected, using pdfplumber for fast extraction")
                return self._process_with_pdfplumber(upload_id, file_path)
            else:
                logger.info("Scanned PDF detected, using OCR pipeline")
                return self._process_with_ocr(upload_id, file_path)
                
        except Exception as e:
            logger.error(f"Processing error: {str(e)}")
            raise
    
    def _process_with_pdfplumber(self, upload_id: str, file_path: str) -> Dict[str, Any]:
        try:
            full_text, tokens = self.pdfplumber_engine.extract_text_from_pdf(file_path)
            
            full_text = self.text_cleaner.clean_text(full_text)
            
            logger.info(f"Extracted text length: {len(full_text)}")
            
            try:
                debug_text_path = Path(self.file_manager.get_processed_dir(upload_id)) / "extracted_text_pdfplumber.txt"
                with open(debug_text_path, 'w', encoding='utf-8') as f:
                    f.write(full_text)
                logger.info(f"Saved extracted text to {debug_text_path}")
            except Exception as e:
                logger.warning(f"Could not save debug text: {str(e)}")
            
            doc_type, type_confidence = self.classifier.classify(full_text, self.template)
            logger.info(f"Classified as: {doc_type} (confidence: {type_confidence})")
            
            extracted_data = self.extractor.extract_bank_statement_fields(full_text, tokens=tokens)
            is_valid, validation_msg = DataValidator.validate_bank_statement(extracted_data, self.template)
            
            confidence = self.extractor.calculate_confidence(extracted_data)
            logger.info(f"Extraction confidence: {confidence}")
            
            document = {
                "document_number": 1,
                "document_type": doc_type,
                "extracted_data": extracted_data,
                "confidence_score": confidence,
                "text_length": len(full_text),
                "extraction_method": "pdfplumber"
            }
            
            config = get_config(self.template)
            
            result = {
                "upload_id": upload_id,
                "file_type": "pdf",
                "total_documents": 1,
                "documents": [document],
                "summary": {
                    "bank_statements": 1 if doc_type == "bank_statement" else 0,
                    "other": 0 if doc_type == "bank_statement" else 1,
                    "average_confidence": round(confidence, 2)
                },
                "processing_completed_at": datetime.now().isoformat(),
                "original_file": f"raw/{upload_id}.pdf",
                "total_text_length": len(full_text),
                "config_version": config.get("config_version", "unknown"),
                "template_used": self.template or "default",
                "extraction_method": "pdfplumber"
            }
            
            logger.info(f"PDFPlumber processing completed for {upload_id}")
            return result
            
        except Exception as e:
            logger.error(f"PDFPlumber processing failed: {str(e)}, falling back to OCR")
            return self._process_with_ocr(upload_id, file_path)
    
    def _process_with_ocr(self, upload_id: str, file_path: str) -> Dict[str, Any]:
        try:
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
            
            max_workers = min(4, len(images))
            logger.info(f"Starting parallel processing with {max_workers} workers")
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_page = {
                    executor.submit(self._process_single_page, doc_num, image_path, upload_id): doc_num
                    for doc_num, image_path in enumerate(images, 1)
                }
                
                for future in as_completed(future_to_page):
                    doc_num = future_to_page[future]
                    try:
                        result = future.result()
                        documents.append(result)
                        confidence_scores.append(result["confidence_score"])
                        total_text_length += result["text_length"]
                        logger.info(f"Completed page {doc_num}")
                    except Exception as e:
                        logger.error(f"Page {doc_num} failed: {str(e)}")
                        raise
            
            documents.sort(key=lambda x: x["document_number"])
            
            documents = StatementMerger.merge_bank_statement_pages(documents)
            
            bank_count = sum(1 for d in documents if d["document_type"] == "bank_statement")
            other_count = len(documents) - bank_count
            
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            
            config = get_config(self.template)
            
            result = {
                "upload_id": upload_id,
                "file_type": "pdf",
                "total_documents": len(documents),
                "documents": documents,
                "summary": {
                    "bank_statements": bank_count,
                    "other": other_count,
                    "average_confidence": round(avg_confidence, 2)
                },
                "processing_completed_at": datetime.now().isoformat(),
                "original_file": f"raw/{upload_id}.pdf",
                "total_text_length": total_text_length,
                "config_version": config.get("config_version", "unknown"),
                "template_used": self.template or "default",
                "extraction_method": "ocr"
            }
            
            logger.info(f"OCR processing completed for {upload_id}")
            return result
        
        except Exception as e:
            logger.error(f"OCR processing error: {str(e)}")
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
