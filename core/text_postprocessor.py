import re
import logging
import logging
from typing import Dict, Any, List
from typing import Dict, Any, List


logger = logging.getLogger(__name__)

class TextPostprocessor:
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get("postprocessing", {})
        self.enabled = self.config.get("enabled", True)
        self.ocr_corrections = self.config.get("ocr_corrections", {})
        
    def process(self, text: str) -> str:
        if not self.enabled:
            return text
        
        original_text = text
        
        try:
            if self.config.get("fix_number_spacing", True):
                text = self._fix_number_spacing(text)
            
            if self.config.get("fix_decimal_points", True):
                text = self._fix_decimal_points(text)
            
            if self.config.get("remove_extra_spaces", True):
                text = self._remove_extra_spaces(text)
            
            if self.config.get("fix_common_ocr_errors", True):
                text = self._fix_ocr_errors(text)
            
            if text != original_text:
                logger.debug(f"Post-processing changed text:\nBefore: {original_text[:100]}\nAfter: {text[:100]}")
            
            return text
            
        except Exception as e:
            logger.error(f"Post-processing failed: {str(e)}")
            return original_text
    
    def process_tokens(self, tokens: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not self.enabled:
            return tokens
        
        processed_tokens = []
        
        for token in tokens:
            processed_token = token.copy()
            original_text = token.get("text", "")
            processed_text = self.process(original_text)
            
            if processed_text != original_text:
                processed_token["text"] = processed_text
                processed_token["original_text"] = original_text
                processed_token["postprocessed"] = True
            
            processed_tokens.append(processed_token)
        
        return processed_tokens
    
    def _fix_number_spacing(self, text: str) -> str:
        try:
            text = re.sub(r'(\d+)\s*,\s*(\d+)', r'\1,\2', text)
            
            text = re.sub(r'(\d+)\s*\.\s*(\d+)', r'\1.\2', text)
            
            def fix_spaced_number(match):
                try:
                    num_str = match.group(0)
                    cleaned = num_str.replace(' ', '')
                    
                    if len(cleaned) >= 4 and ',' not in cleaned and '.' not in cleaned:
                        if len(cleaned) == 5:
                            return cleaned[:2] + ',' + cleaned[2:]
                        elif len(cleaned) == 6:
                            return cleaned[:3] + ',' + cleaned[3:]
                        elif len(cleaned) == 7:
                            return cleaned[:1] + ',' + cleaned[1:4] + ',' + cleaned[4:]
                    
                    return cleaned
                except Exception as e:
                    logger.debug(f"Error in fix_spaced_number: {e}")
                    return match.group(0)
            
            text = re.sub(r'\b\d+(?:\s+\d+)+\b', fix_spaced_number, text)
            
        except Exception as e:
            logger.error(f"Error in _fix_number_spacing: {e}")
        
        return text
    
    def _fix_decimal_points(self, text: str) -> str:
        try:
            text = re.sub(r'(\d{1,3}(?:,\d{3})*)\s+(\d{2})(?=\s|$|\n)', r'\1.\2', text)
            
            text = re.sub(r'(\d+)\.(?=\s|$|\n)', r'\1.00', text)
        except Exception as e:
            logger.error(f"Error in _fix_decimal_points: {e}")
        
        return text
    
    def _remove_extra_spaces(self, text: str) -> str:
        text = re.sub(r' {2,}', ' ', text)
        
        text = re.sub(r'\s+([.,;:])', r'\1', text)
        
        text = re.sub(r'([\(\[])\s+', r'\1', text)
        
        text = re.sub(r'\s+([\)\]])', r'\1', text)
        
        return text
    
    def _fix_ocr_errors(self, text: str) -> str:
        try:
            for wrong, correct in self.ocr_corrections.items():
                try:
                    pattern = r'(\d)' + re.escape(wrong) + r'(\d)'
                    text = re.sub(pattern, r'\1' + correct + r'\2', text)
                    
                    pattern = r'\b' + re.escape(wrong) + r'(\d+)'
                    text = re.sub(pattern, correct + r'\1', text)
                    
                    pattern = r'(\d+)' + re.escape(wrong) + r'\b'
                    text = re.sub(pattern, r'\1' + correct, text)
                except Exception as e:
                    logger.debug(f"Error fixing OCR error for '{wrong}': {e}")
                    continue
        except Exception as e:
            logger.error(f"Error in _fix_ocr_errors: {e}")
        
        return text
    
    def clean_currency_value(self, value: str) -> str:
        if not value:
            return "0.00"
        
        value = re.sub(r'[RM$€£¥]', '', value)
        
        value = value.replace(' ', '')
        
        value = self._fix_decimal_points(value)
        value = self._fix_number_spacing(value)
        
        match = re.search(r'[\d,]+\.?\d*', value)
        if match:
            value = match.group(0)
            value = value.replace(',', '')
            
            if '.' not in value:
                value += '.00'
            elif len(value.split('.')[1]) == 1:
                value += '0'
            
            return value
        
        return "0.00"
