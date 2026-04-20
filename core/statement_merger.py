import logging
from typing import List, Dict, Any, Optional
from typing import List, Dict, Any, Optional


logger = logging.getLogger(__name__)

class StatementMerger:
    
    @staticmethod
    def merge_bank_statement_pages(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        
        if not documents:
            return documents
        
        bank_statements = [d for d in documents if d.get("document_type") == "bank_statement"]
        other_docs = [d for d in documents if d.get("document_type") != "bank_statement"]
        
        if len(bank_statements) <= 1:
            return documents
        
        merged_statements = []
        current_group = []
        
        for i, doc in enumerate(bank_statements):
            extracted = doc.get("extracted_data", {})
            account_num = extracted.get("account_number")
            
            if not current_group:
                current_group.append(doc)
                continue
            
            prev_doc = current_group[-1]
            prev_extracted = prev_doc.get("extracted_data", {})
            prev_account = prev_extracted.get("account_number")
            
            if account_num == prev_account and account_num:
                current_group.append(doc)
            else:
                merged = StatementMerger._merge_group(current_group)
                merged_statements.append(merged)
                current_group = [doc]
        
        if current_group:
            merged = StatementMerger._merge_group(current_group)
            merged_statements.append(merged)
        
        logger.info(f"Merged {len(bank_statements)} pages into {len(merged_statements)} statements")
        
        return merged_statements + other_docs
    
    @staticmethod
    def _merge_group(group: List[Dict[str, Any]]) -> Dict[str, Any]:
        
        if len(group) == 1:
            return group[0]
        
        first_page = group[0]
        last_page = group[-1]
        
        first_data = first_page.get("extracted_data", {})
        last_data = last_page.get("extracted_data", {})
        
        opening_balance = first_data.get("opening_balance", "0.00")
        
        closing_balance = "0.00"
        for doc in reversed(group):
            cb = doc.get("extracted_data", {}).get("closing_balance")
            if cb and cb != "0.00":
                closing_balance = cb
                logger.info(f"Found closing balance {closing_balance} from page {doc.get('document_number')}")
                break
        
        total_debit = None
        total_credit = None
        available_balance = None
        statement_period_from = None
        statement_period_to = None
        
        for doc in group:
            data = doc.get("extracted_data", {})
            if data.get("total_debit") and not total_debit:
                total_debit = data.get("total_debit")
            if data.get("total_credit") and not total_credit:
                total_credit = data.get("total_credit")
            if data.get("available_balance"):
                available_balance = data.get("available_balance")
            if data.get("statement_period_from") and not statement_period_from:
                statement_period_from = data.get("statement_period_from")
            if data.get("statement_period_to"):
                statement_period_to = data.get("statement_period_to")
        
        merged_data = {
            "account_holder_name": first_data.get("account_holder_name"),
            "account_number": first_data.get("account_number"),
            "statement_date": first_data.get("statement_date"),
            "opening_balance": opening_balance,
            "closing_balance": closing_balance,
            "available_balance": available_balance,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "statement_period_from": statement_period_from,
            "statement_period_to": statement_period_to,
            "page_count": len(group)
        }
        
        total_text_length = sum(doc.get("text_length", 0) for doc in group)
        avg_confidence = sum(doc.get("confidence_score", 0) for doc in group) / len(group)
        
        merged_doc = {
            "document_number": first_page.get("document_number"),
            "document_type": "bank_statement",
            "extracted_data": merged_data,
            "confidence_score": round(avg_confidence, 2),
            "text_length": total_text_length,
            "is_merged": True,
            "merged_from_pages": len(group)
        }
        
        page_numbers = [doc.get("document_number") for doc in group]
        logger.info(f"Merged pages {page_numbers} into single statement")
        logger.info(f"Opening: {opening_balance}, Closing: {closing_balance}")
        
        return merged_doc
