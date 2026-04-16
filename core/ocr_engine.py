from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)

class OCREngine(ABC):
    
    @abstractmethod
    def extract_text(self, image_path: str) -> str:
        pass
    
    @abstractmethod
    def extract_text_with_coordinates(self, image_path: str) -> List[Dict[str, Any]]:
        pass

class PaddleOCREngine(OCREngine):
    
    def __init__(self, language: str = "en"):
        try:
            import os
            os.environ['PADDLE_DEVICE'] = 'cpu'
            os.environ['PADDLE_DISABLE_ONEDNN'] = '1'
            os.environ['PADDLE_DISABLE_FAST_MATH'] = '1'
            
            from paddleocr import PaddleOCR
            self.ocr = PaddleOCR(use_angle_cls=False, lang=language)
            logger.info("PaddleOCR initialized successfully")
        except ImportError:
            logger.error("PaddleOCR not installed. Install with: pip install paddleocr")
            raise
    
    def extract_text(self, image_path: str) -> str:
        try:
            result = self.ocr.ocr(image_path)
            text = "\n".join([line[0][1] for line in result[0]])
            return text
        except Exception as e:
            logger.error(f"PaddleOCR extraction error: {str(e)}")
            raise
    
    def extract_text_with_coordinates(self, image_path: str) -> List[Dict[str, Any]]:
        try:
            result = self.ocr.ocr(image_path)
            extracted = []
            for line in result[0]:
                bbox, (text, confidence) = line
                extracted.append({
                    "text": text,
                    "confidence": confidence,
                    "bbox": bbox
                })
            return extracted
        except Exception as e:
            logger.error(f"PaddleOCR coordinate extraction error: {str(e)}")
            raise

class EasyOCREngine(OCREngine):
    
    def __init__(self, language: str = "en"):
        try:
            import easyocr
            self.reader = easyocr.Reader([language])
            logger.info("EasyOCR initialized successfully")
        except ImportError:
            logger.error("EasyOCR not installed. Install with: pip install easyocr")
            raise
    
    def extract_text(self, image_path: str) -> str:
        try:
            result = self.reader.readtext(image_path)
            text = "\n".join([item[1] for item in result])
            return text
        except Exception as e:
            logger.error(f"EasyOCR extraction error: {str(e)}")
            raise
    
    def extract_text_with_coordinates(self, image_path: str) -> List[Dict[str, Any]]:
        try:
            result = self.reader.readtext(image_path)
            extracted = []
            for item in result:
                bbox, text, confidence = item
                extracted.append({
                    "text": text,
                    "confidence": confidence,
                    "bbox": bbox
                })
            return extracted
        except Exception as e:
            logger.error(f"EasyOCR coordinate extraction error: {str(e)}")
            raise

class TesseractOCREngine(OCREngine):
    
    def __init__(self, language: str = "eng"):
        try:
            import pytesseract
            self.pytesseract = pytesseract
            self.language = language
            logger.info("Tesseract OCR initialized successfully")
        except ImportError:
            logger.error("pytesseract not installed. Install with: pip install pytesseract")
            raise
    
    def extract_text(self, image_path: str) -> str:
        try:
            text = self.pytesseract.image_to_string(image_path, lang=self.language)
            return text
        except Exception as e:
            logger.error(f"Tesseract extraction error: {str(e)}")
            raise
    
    def extract_text_with_coordinates(self, image_path: str) -> List[Dict[str, Any]]:
        try:
            data = self.pytesseract.image_to_data(image_path, lang=self.language, output_type='dict')
            extracted = []
            for i in range(len(data['text'])):
                if data['text'][i].strip():
                    extracted.append({
                        "text": data['text'][i],
                        "confidence": data['conf'][i] / 100.0,
                        "bbox": [
                            [data['left'][i], data['top'][i]],
                            [data['left'][i] + data['width'][i], data['top'][i]],
                            [data['left'][i] + data['width'][i], data['top'][i] + data['height'][i]],
                            [data['left'][i], data['top'][i] + data['height'][i]]
                        ]
                    })
            return extracted
        except Exception as e:
            logger.error(f"Tesseract coordinate extraction error: {str(e)}")
            raise

def get_ocr_engine(engine_name: str = "paddleocr", language: str = "en") -> OCREngine:
    engine_name = engine_name.lower()
    
    if engine_name == "paddleocr":
        return PaddleOCREngine(language)
    elif engine_name == "easyocr":
        return EasyOCREngine(language)
    elif engine_name == "tesseract":
        return TesseractOCREngine(language)
    else:
        raise ValueError(f"Unknown OCR engine: {engine_name}")
