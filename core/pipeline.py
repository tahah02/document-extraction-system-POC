import logging
from typing import Dict, Any, List, Optional
from typing import Dict, Any, List, Optional
from datetime import datetime
from datetime import datetime
import json
import json
from pathlib import Path
from pathlib import Path

from core.ocr_engine import get_ocr_engine
from core.document_classifier import DocumentClassifier
from core.document_classifier import DocumentClassifier
from core.extractor import FieldExtractor
from core.extractor import FieldExtractor
from core.validators import DataValidator
from core.validators import DataValidator
from core.config import get_config
from core.config import get_config
from core.statement_merger import StatementMerger
from core.statement_merger import StatementMerger
from utils.pdf_processor import PDFProcessor
from utils.pdf_processor import PDFProcessor
from utils.text_cleaner import TextCleaner
from utils.text_cleaner import TextCleaner
from utils.file_manager import FileManager
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
                total_text_length += len(text)
                
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
                confidence_scores.append(confidence)
                
                logger.info(f"Extraction confidence: {confidence}")
                
                documents.append({
                    "document_number": doc_num,
                    "document_type": doc_type,
                    "extracted_data": extracted_data,
                    "confidence_score": confidence,
                    "text_length": len(text)
                })
            
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
                "template_used": self.template or "default"
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
