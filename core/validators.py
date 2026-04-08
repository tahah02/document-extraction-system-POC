import logging
import re
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

class DataValidator:
    
    @staticmethod
    def validate_payslip(data: Dict[str, Any]) -> Tuple[bool, str]:
        try:
            required_fields = ["name", "id_number", "gross_income", "net_income", "total_deduction", "month_year"]
            missing_fields = [f for f in required_fields if not data.get(f)]
            
            if missing_fields:
                return False, f"Missing fields: {', '.join(missing_fields)}"
            
            if not DataValidator._validate_id_number(data["id_number"]):
                return False, "Invalid ID number format"
            
            if not DataValidator._validate_currency(data["gross_income"]):
                return False, "Invalid gross income format"
            
            if not DataValidator._validate_currency(data["net_income"]):
                return False, "Invalid net income format"
            
            if not DataValidator._validate_currency(data["total_deduction"]):
                return False, "Invalid total deduction format"
            
            if not DataValidator._validate_month_year(data["month_year"]):
                return False, "Invalid month/year format"
            
            return True, "Valid payslip data"
        
        except Exception as e:
            logger.error(f"Payslip validation error: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def validate_bank_statement(data: Dict[str, Any]) -> Tuple[bool, str]:
        try:
            required_fields = ["account_holder_name", "account_number", "statement_date", "opening_balance", "closing_balance"]
            missing_fields = [f for f in required_fields if not data.get(f)]
            
            if missing_fields:
                return False, f"Missing fields: {', '.join(missing_fields)}"
            
            if not DataValidator._validate_account_number(data["account_number"]):
                return False, "Invalid account number format"
            
            if not DataValidator._validate_date(data["statement_date"]):
                return False, "Invalid statement date format"
            
            if not DataValidator._validate_currency(data["opening_balance"]):
                return False, "Invalid opening balance format"
            
            if not DataValidator._validate_currency(data["closing_balance"]):
                return False, "Invalid closing balance format"
            
            return True, "Valid bank statement data"
        
        except Exception as e:
            logger.error(f"Bank statement validation error: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def _validate_id_number(id_number: str) -> bool:
        pattern = r"^\d{6}-\d{2}-\d{4}$"
        return bool(re.match(pattern, id_number.strip()))
    
    @staticmethod
    def _validate_currency(value: str) -> bool:
        cleaned = value.replace(",", "").strip()
        pattern = r"^\d+\.\d{2}$"
        return bool(re.match(pattern, cleaned))
    
    @staticmethod
    def _validate_month_year(value: str) -> bool:
        pattern = r"^\d{2}/\d{4}$"
        if not re.match(pattern, value.strip()):
            return False
        
        month = int(value.split("/")[0])
        return 1 <= month <= 12
    
    @staticmethod
    def _validate_account_number(account_number: str) -> bool:
        pattern = r"^\d{2}-\d{7}-\d$"
        return bool(re.match(pattern, account_number.strip()))
    
    @staticmethod
    def _validate_date(date_str: str) -> bool:
        pattern = r"^\d{2}/\d{2}/\d{4}$"
        if not re.match(pattern, date_str.strip()):
            return False
        
        day, month, year = date_str.split("/")
        day, month, year = int(day), int(month), int(year)
        
        return 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2100
