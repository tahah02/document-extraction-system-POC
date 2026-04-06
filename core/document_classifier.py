import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class DocumentClassifier:
    
    PAYSLIP_KEYWORDS = [
        "payslip", "salary", "gross", "net income", "deduction",
        "employee", "month", "year", "eis", "socso", "epf",
        "income tax", "allowance", "overtime", "basic salary",
        "nric", "id number", "employee id", "department",
        "pay period", "payment date", "total deduction",
        "employer", "employee name", "designation",
        # Malay keywords
        "gaji", "gaji pokok", "gaji bersih", "cukai pendapatan",
        "kwsp", "perkeso", "takaful", "potongan", "pendapatan",
        "jumlah", "bulan", "nama", "no k/p", "no gaji"
    ]
    
    BANK_STATEMENT_KEYWORDS = [
        "bank statement", "account", "balance", "transaction",
        "deposit", "withdrawal", "statement date", "account number",
        "opening balance", "closing balance", "statement period",
        "bank name", "account holder", "date", "amount",
        "reference", "description", "debit", "credit",
        "statement of account", "account summary"
    ]
    
    @staticmethod
    def classify(text: str) -> Tuple[str, float]:
        text_lower = text.lower()
        
        payslip_matches = sum(1 for keyword in DocumentClassifier.PAYSLIP_KEYWORDS 
                             if keyword in text_lower)
        bank_matches = sum(1 for keyword in DocumentClassifier.BANK_STATEMENT_KEYWORDS 
                          if keyword in text_lower)
        
        total_matches = payslip_matches + bank_matches
        
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
            return "unknown", 0.5
    
    @staticmethod
    def is_payslip(text: str, threshold: float = 0.5) -> bool:
        doc_type, confidence = DocumentClassifier.classify(text)
        return doc_type == "payslip" and confidence >= threshold
    
    @staticmethod
    def is_bank_statement(text: str, threshold: float = 0.5) -> bool:
        doc_type, confidence = DocumentClassifier.classify(text)
        return doc_type == "bank_statement" and confidence >= threshold
