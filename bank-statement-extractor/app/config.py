from pydantic_settings import BaseSettings
from typing import List
from typing import List
import os
import os


class Settings(BaseSettings):
    
    API_TITLE: str = "Document Extraction System"
    API_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    HOST: str = "0.0.0.0"
    PORT: int = 8004
    
    CORS_ORIGINS: List[str] = ["*"]
    
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024
    UPLOAD_DIR: str = "uploads"
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "jpg", "jpeg", "png", "docx", "doc"]
    
    OCR_ENGINE: str = os.getenv("OCR_ENGINE", "paddleocr")
    OCR_LANGUAGE: str = "en"
    OCR_CONFIDENCE_THRESHOLD: float = 0.5
    
    OUTPUT_DIR: str = "output"
    TEMP_DIR: str = "temp"
    
    MIN_CONFIDENCE_SCORE: float = 0.95
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()
