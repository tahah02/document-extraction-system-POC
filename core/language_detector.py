import logging
from typing import Tuple, Dict
from typing import Tuple, Dict


logger = logging.getLogger(__name__)

class LanguageDetector:
    LANGUAGE_KEYWORDS = {
        "en": {
            "common": ["the", "and", "is", "to", "of", "in", "for", "that", "with", "a", "on"],
            "bank": ["account", "balance", "transaction", "deposit", "withdrawal", "statement"]
        },
        "ms": {
            "common": ["yang", "dan", "adalah", "untuk", "di", "pada", "dengan", "dari", "ke", "ini"],
            "bank": ["akaun", "baki", "transaksi", "pengeluaran", "deposit", "penyata", "tarikh"]
        },
        "ar": {
            "common": ["في", "من", "إلى", "هو", "هي", "و", "أن", "على", "عن", "كل"],
            "bank": ["حساب", "الرصيد", "معاملة", "إيداع", "سحب", "كشف", "التاريخ"]
        }
    }
    
    @staticmethod
    def detect_language(text: str) -> Tuple[str, float]:
        if not text or len(text.strip()) < 10:
            return "en", 0.0
        
        try:
            return LanguageDetector._keyword_based_detection(text)
        except Exception as e:
            logger.warning(f"Language detection failed: {str(e)}, defaulting to English")
            return "en", 0.0
    
    @staticmethod
    def _keyword_based_detection(text: str) -> Tuple[str, float]:
        text_lower = text.lower()
        scores = {}
        
        for lang, keywords_dict in LanguageDetector.LANGUAGE_KEYWORDS.items():
            all_keywords = (
                keywords_dict.get("common", []) +
                keywords_dict.get("bank", [])
            )
            
            matches = sum(1 for keyword in all_keywords if keyword in text_lower)
            scores[lang] = matches
        
        if not scores or max(scores.values()) == 0:
            return "en", 0.0
        
        best_lang = max(scores, key=scores.get)
        total_matches = sum(scores.values())
        confidence = scores[best_lang] / total_matches if total_matches > 0 else 0.0
        
        return best_lang, round(confidence, 2)
    
    @staticmethod
    def get_supported_languages() -> list:
        return list(LanguageDetector.LANGUAGE_KEYWORDS.keys())
