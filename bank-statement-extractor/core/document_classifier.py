import logging
from typing import Tuple
from typing import Tuple
from core.config import get_classification_config
from core.config import get_classification_config


logger = logging.getLogger(__name__)

class DocumentClassifier:
    
    @staticmethod
    def classify(text: str, template: str = None) -> Tuple[str, float]:
        return "bank_statement", 1.0
    
    @staticmethod
    def is_bank_statement(text: str, template: str = None) -> bool:
        return True
