import re
import logging

logger = logging.getLogger(__name__)


class CurrencyFormatter:
   
    
    @staticmethod
    def clean_currency(value: str) -> str:
       
        if not value or not isinstance(value, str):
            return "0.00"
        
        value = value.strip()       
        if not value:
            return "0.00"
       
        comma_count = value.count(",")
        dot_count = value.count(".")        
        if dot_count > 0:
            
            value = value.replace(",", "").replace(" ", "")
        elif comma_count > 0:
            value_no_space = value.replace(" ", "")
            last_comma_pos = value_no_space.rfind(",")
            digits_after_comma = len(value_no_space) - last_comma_pos - 1
            
            if digits_after_comma == 5:
                value = value_no_space.replace(",", "")
             
                if len(value) >= 2:
                    value = value[:-2] + "." + value[-2:]
            elif digits_after_comma == 2:
             
                value = value_no_space.replace(",", "")
            else:
              
                value = value_no_space.replace(",", "")
        else:
            
            value = value.replace(" ", "")
             
        value = re.sub(r"[^\d.]", "", value)
       
        if not value:
            return "0.00"
            
        if value.count(".") > 1:
            parts = value.split(".")
            value = "".join(parts[:-1]) + "." + parts[-1]        
        try:
            numeric_value = float(value)
            return f"{numeric_value:.2f}"
        except ValueError:
            logger.warning(f"Could not convert '{value}' to float, returning 0.00")
            return "0.00"


    @staticmethod
    def clean_id_number(value: str) -> str:
        if not value or not isinstance(value, str):
            return ""   
        digits = re.sub(r"\D", "", value.strip())       
        if len(digits) == 12:
            return f"{digits[:6]}-{digits[6:8]}-{digits[8:12]}"
        
        return value.strip()


    @staticmethod
    def clean_month_year(value: str) -> str:
    
        if not value or not isinstance(value, str):
            return ""
        
        value = value.strip()
        match = re.search(r"(\d{1,2})[/-]?(\d{4})", value)
        
        if match:
            month = int(match.group(1))
            year = match.group(2)

            if 1 <= month <= 12:
                return f"{month:02d}/{year}"
        
        return value
