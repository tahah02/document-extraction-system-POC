import logging
from typing import Tuple
from typing import Tuple
from core.config import get_classification_config
from core.config import get_classification_config


logger = logging.getLogger(__name__)

class DocumentClassifier:
    
    @staticmethod
    def classify(text: str, template: str = None) -> Tuple[str, float]:
        config = get_classification_config(template)
        min_keyword_matches = config.get("min_keyword_matches", 1)
        unknown_confidence = config.get("unknown_confidence", 0.5)
        payslip_keywords = config.get("payslip_keywords", [])
        bank_keywords = config.get("bank_statement_keywords", [])
        
        text_lower = text.lower()
        
        payslip_matches = sum(1 for keyword in payslip_keywords if keyword in text_lower)
        bank_matches = sum(1 for keyword in bank_keywords if keyword in text_lower)
        
        total_matches = payslip_matches + bank_matches
        
        if total_matches < min_keyword_matches:
            logger.warning(f"Insufficient keyword matches: {total_matches} < {min_keyword_matches}")
            return "unknown", 0.0
        
        if total_matches == 0:
            logger.warning("No document type keywords found")
            return "unknown", 0.0
        
        if payslip_matches > bank_matches:
            confidence = payslip_matches / total_matches
            return "payslip", confidence
        elif bank_matches > payslip_matches:
            confidence = bank_matches / total_matches
            return "bank_statement", confidence
        else:
            return "unknown", unknown_confidence
    
    @staticmethod
    def is_payslip(text: str, template: str = None) -> bool:
        config = get_classification_config(template)
        threshold = config.get("threshold", 0.5)
        doc_type, confidence = DocumentClassifier.classify(text, template)
        return doc_type == "payslip" and confidence >= threshold
    
    @staticmethod
    def is_bank_statement(text: str, template: str = None) -> bool:
        config = get_classification_config(template)
        threshold = config.get("threshold", 0.5)
        doc_type, confidence = DocumentClassifier.classify(text, template)
        return doc_type == "bank_statement" and confidence >= threshold
