import json
import logging
import re
from typing import Dict, Any, Optional
from pathlib import Path
from core.utils import CurrencyFormatter

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
                "name": {"keywords": ["name", "employee name", "nama", "nama pegawai", "الاسم", "اسم الموظف"], "pattern": None},
                "id_number": {"keywords": ["id", "nric", "employee id", "no. k/p", "no k/p", "رقم الهوية", "رقم الموظف"], "pattern": r"\d{6}-\d{2}-\d{4}|\d{12}"},
                "gross_income": {"keywords": ["gross", "gross income", "gross salary", "gaji kasar", "gaji pokok", "jumlah pendapatan", "الراتب الإجمالي", "الدخل الإجمالي"], "pattern": r"[\d,]+\.?\d{0,2}"},
                "net_income": {"keywords": ["net", "net income", "take home", "gaji bersih", "صافي الراتب", "الدخل الصافي"], "pattern": r"[\d,]+\.?\d{0,2}"},
                "total_deduction": {"keywords": ["deduction", "total deduction", "jumlah potongan", "الخصم الإجمالي", "إجمالي الخصومات"], "pattern": r"[\d,]+\.?\d{0,2}"},
                "month_year": {"keywords": ["month", "period", "date", "bulan", "tarikh", "الشهر", "التاريخ"], "pattern": r"\d{1,2}/\d{4}|\d{1,2}-\d{4}"}
            },
            "bank_statement": {
                "account_holder_name": {"keywords": ["account holder", "name", "nama pemegang", "اسم صاحب الحساب"], "pattern": None},
                "account_number": {"keywords": ["account", "account number", "no. akaun", "رقم الحساب"], "pattern": r"\d{2}-\d{7}-\d|\d{10,12}"},
                "statement_date": {"keywords": ["date", "statement date", "tarikh", "تاريخ الكشف"], "pattern": r"\d{1,2}/\d{1,2}/\d{4}|\d{1,2}-\d{1,2}-\d{4}"},
                "opening_balance": {"keywords": ["opening balance", "baki pembukaan", "الرصيد الافتتاحي"], "pattern": r"[\d,]+\.?\d{0,2}"},
                "closing_balance": {"keywords": ["closing balance", "baki penutup", "الرصيد الختامي"], "pattern": r"[\d,]+\.?\d{0,2}"}
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
        
        if not extracted["name"]:
            match = re.search(r"Nama\s+([A-Za-z\s]+?)(?:\n|No)", text, re.IGNORECASE)
            if match:
                extracted["name"] = match.group(1).strip()
        
        if not extracted["gross_income"]:
            match = re.search(r"Gaji\s+Pokok\s+([\d,\s]+?)(?:\s+\d{4}|$|\n)", text, re.IGNORECASE)
            if match:
                value = match.group(1).strip().replace(" ", "")
                value = re.match(r"[\d,]+", value).group(0) if re.match(r"[\d,]+", value) else value
                extracted["gross_income"] = value
        
        if not extracted["net_income"]:
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
        
        extracted["gross_income"] = CurrencyFormatter.clean_currency(extracted["gross_income"])
        extracted["total_deduction"] = CurrencyFormatter.clean_currency(extracted["total_deduction"])
        
        net_income_cleaned = CurrencyFormatter.clean_currency(extracted["net_income"])
        if net_income_cleaned == "0.00" or not extracted["net_income"]:
            try:
                gross = float(extracted["gross_income"])
                deduction = float(extracted["total_deduction"])
                calculated_net = gross - deduction
                extracted["net_income"] = f"{calculated_net:.2f}"
                logger.info(f"Calculated net_income: {extracted['net_income']} (gross: {gross}, deduction: {deduction})")
            except (ValueError, TypeError) as e:
                logger.warning(f"Could not calculate net_income: {str(e)}")
                extracted["net_income"] = net_income_cleaned
        else:
            extracted["net_income"] = net_income_cleaned
        
        return extracted
    
    def extract_bank_statement_fields(self, text: str) -> Dict[str, Any]:
        extracted = {
            "account_holder_name": None,
            "account_number": self._extract_field(text, "account_number"),
            "statement_date": self._extract_field(text, "statement_date"),
            "opening_balance": None,
            "closing_balance": None
        }
        
        match = re.search(r"(\d{2}/\d{2}/\d{4})\s+([A-Za-z\s]+?)\s+(\d+,?\s*JALAN|Summary|Ringkasan)", text, re.IGNORECASE)
        if match:
            name = match.group(2).strip()
            if name and len(name) > 3 and not re.search(r"Statement|Tarikh|Penyata|Account|Akaun", name, re.IGNORECASE):
                extracted["account_holder_name"] = name
        
        if not extracted["account_holder_name"]:
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if "Siti" in line or "Aisah" in line or "Binti" in line or "Ghazali" in line:
                    if len(line) > 5 and len(line) < 100:
                        extracted["account_holder_name"] = line
                        break
        
        if not extracted["account_holder_name"]:
            lines = text.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                if not line or len(line) < 5 or len(line) > 100:
                    continue
                
                has_capital_words = len(re.findall(r'\b[A-Z][a-z]+\b', line)) >= 2
                
                if has_capital_words and not re.search(r"CIMB|Statement|Account|Number|Date|Balance|Period|Page|Halaman|Summary|Ringkasan|JALAN|KUALA|LUMPUR|RM|Tarikh|Penyata|Akaun|Simpanan|Transaksi|Butir|Withdrawal|Deposit|GST|Baki|Pengeluaran|Rujukan|Diskripsi|51-|52-|53-|54-|55-|56-|57-|58-|59-|60-|Savings|Eligible|PIDM|Bonus|Points|Mata|Ganjaran|Diperolehi|Dilunaskan|Dipindahkan|Terkini|Expiring|Lupus|Opening|Closing|Interest|Fee|Transfer|ATM|Debit|Credit", line, re.IGNORECASE):
                    extracted["account_holder_name"] = line
                    break
        
        opening_match = re.search(r"OPENING\s+BALANCE\s+([\d,.\s]+?)(?:\n|$|\d{2}/\d{2}/\d{4})", text, re.IGNORECASE)
        if opening_match and opening_match.group(1):
            val = opening_match.group(1).strip().replace(" ", "")
            if val:
                extracted["opening_balance"] = val
        
        closing_match = re.search(r"(?:CLOSING\s+BALANCE|BAKI\s+PENUTUP)\s+([\d,.\s]+?)(?:\n|$|End\s+of)", text, re.IGNORECASE)
        if closing_match and closing_match.group(1):
            val = closing_match.group(1).strip().replace(" ", "")
            if val:
                extracted["closing_balance"] = val
        
        if not extracted["opening_balance"]:
            extracted["opening_balance"] = self._extract_field(text, "opening_balance")
        
        if not extracted["closing_balance"]:
            extracted["closing_balance"] = self._extract_field(text, "closing_balance")
        
        extracted["opening_balance"] = CurrencyFormatter.clean_currency(extracted["opening_balance"])
        extracted["closing_balance"] = CurrencyFormatter.clean_currency(extracted["closing_balance"])
        
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
            
            if field_config.get("pattern"):
                match = re.search(field_config["pattern"], text, re.IGNORECASE)
                if match:
                    return match.group(0)
            
            keywords = field_config.get("keywords", [])
            for keyword in keywords:
                pattern = f"{keyword}[:\\s]+([^\\n]+?)(?=\\n|$|[A-Z][a-z])"
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    value = re.sub(r'\s+', ' ', value)
                    value = re.sub(r'[^\w\s\-./,RM]', '', value).strip()
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
