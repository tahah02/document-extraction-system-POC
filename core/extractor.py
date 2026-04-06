import json
import logging
import re
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class FieldExtractor:
    
    def __init__(self, config_path: str = "config/extraction_config.json"):
        self.config = self._load_config(config_path)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        try:
            if Path(config_path).exists():
                with open(config_path, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"Config file not found: {config_path}, using defaults")
                return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        return {
            "payslip": {
                "name": {"keywords": ["name", "employee name", "nama", "nama pegawai"], "pattern": None},
                "id_number": {"keywords": ["id", "nric", "employee id", "no. k/p", "no k/p"], "pattern": r"\d{6}-\d{2}-\d{4}|\d{12}"},
                "gross_income": {"keywords": ["gross", "gross income", "gross salary", "gaji kasar", "gaji pokok", "jumlah pendapatan"], "pattern": r"[\d,]+\.?\d{0,2}"},
                "net_income": {"keywords": ["net", "net income", "take home", "gaji bersih"], "pattern": r"[\d,]+\.?\d{0,2}"},
                "total_deduction": {"keywords": ["deduction", "total deduction", "jumlah potongan"], "pattern": r"[\d,]+\.?\d{0,2}"},
                "month_year": {"keywords": ["month", "period", "date", "bulan", "tarikh"], "pattern": r"\d{1,2}/\d{4}|\d{1,2}-\d{4}"}
            },
            "bank_statement": {
                "account_holder_name": {"keywords": ["account holder", "name", "nama pemegang"], "pattern": None},
                "account_number": {"keywords": ["account", "account number", "no. akaun"], "pattern": r"\d{2}-\d{7}-\d|\d{10,12}"},
                "statement_date": {"keywords": ["date", "statement date", "tarikh"], "pattern": r"\d{1,2}/\d{1,2}/\d{4}|\d{1,2}-\d{1,2}-\d{4}"}
            }
        }
    
    def extract_payslip_fields(self, text: str) -> Dict[str, Any]:
        extracted = {
            "name": self._extract_field(text, "name"),
            "id_number": self._extract_field(text, "id_number"),
            "gross_income": self._extract_field(text, "gross_income"),
            "net_income": self._extract_field(text, "net_income"),
            "total_deduction": self._extract_field(text, "total_deduction"),
            "month_year": self._extract_field(text, "month_year")
        }
        
        # Fallback: Try direct pattern matching for Malay payslips
        if not extracted["name"]:
            match = re.search(r"Nama\s+([A-Za-z\s]+?)(?:\n|No)", text, re.IGNORECASE)
            if match:
                extracted["name"] = match.group(1).strip()
        
        if not extracted["gross_income"]:
            match = re.search(r"Gaji\s+Pokok\s+([\d,\s]+?)(?:\s+\d{4}|$|\n)", text, re.IGNORECASE)
            if match:
                value = match.group(1).strip().replace(" ", "")
                # Keep only first number
                value = re.match(r"[\d,]+", value).group(0) if re.match(r"[\d,]+", value) else value
                extracted["gross_income"] = value
        
        if not extracted["net_income"]:
            # Try multiple patterns for net income
            patterns = [
                r"Gaji\s+Bersih\s+([\d,\s]+?)(?:\n|Pendapatan)",
                r"Gaji\s+Bersih\s+([\d,\s]+?)$"
            ]
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1).strip().replace(" ", "")
                    if value:
                        extracted["net_income"] = value
                        break
        
        if not extracted["total_deduction"]:
            match = re.search(r"Jumlah\s+Potongan\s+([\d\s,]+)", text, re.IGNORECASE)
            if match:
                extracted["total_deduction"] = match.group(1).strip().replace(" ", "")
        
        return extracted
    
    def extract_bank_statement_fields(self, text: str) -> Dict[str, Any]:
        extracted = {
            "account_holder_name": self._extract_field(text, "account_holder_name"),
            "account_number": self._extract_field(text, "account_number"),
            "statement_date": self._extract_field(text, "statement_date")
        }
        
        # Fallback: Try direct pattern matching for bank statements
        if not extracted["account_holder_name"]:
            # Try multiple patterns
            patterns = [
                r"Account\s+Holder[:\s]+([A-Za-z\s]+?)(?:\n|Account)",
                r"Name[:\s]+([A-Za-z\s]+?)(?:\n|Account)",
                r"^([A-Za-z\s]+?)\s+Account",
            ]
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    if len(value) > 2:
                        extracted["account_holder_name"] = value
                        break
        
        # Clean up account holder name
        if extracted["account_holder_name"]:
            # Remove "CIMB BANK" and "Statement of" etc
            name = extracted["account_holder_name"]
            name = re.sub(r"CIMB\s+BANK|Statement\s+of|Account\s+Holder", "", name, flags=re.IGNORECASE)
            name = name.strip()
            if name:
                extracted["account_holder_name"] = name
        
        return extracted
    
    def _extract_field(self, text: str, field_name: str) -> Optional[str]:
        try:
            if field_name in self.config.get("payslip", {}):
                field_config = self.config["payslip"][field_name]
            elif field_name in self.config.get("bank_statement", {}):
                field_config = self.config["bank_statement"][field_name]
            else:
                logger.warning(f"Field not found in config: {field_name}")
                return None
            
            # Try pattern matching first
            if field_config.get("pattern"):
                match = re.search(field_config["pattern"], text, re.IGNORECASE)
                if match:
                    return match.group(0)
            
            # Try keyword-based extraction
            keywords = field_config.get("keywords", [])
            for keyword in keywords:
                # More flexible pattern to handle spaces and formatting
                pattern = f"{keyword}[:\\s]+([^\\n]+?)(?=\\n|$|[A-Z][a-z])"
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    # Clean up the value
                    value = re.sub(r'\s+', ' ', value)  # Normalize spaces
                    value = re.sub(r'[^\w\s\-./,RM]', '', value).strip()  # Keep important chars
                    if value and len(value) > 1:
                        return value
            
            return None
        
        except Exception as e:
            logger.error(f"Error extracting field {field_name}: {str(e)}")
            return None
    
    def calculate_confidence(self, extracted_data: Dict[str, Any]) -> float:
        if not extracted_data:
            return 0.0
        
        total_fields = len(extracted_data)
        filled_fields = sum(1 for v in extracted_data.values() if v is not None)
        
        confidence = filled_fields / total_fields if total_fields > 0 else 0.0
        return round(confidence, 2)
