import os
import shutil
import shutil
from pathlib import Path
from pathlib import Path
from typing import List
from typing import List
import logging
import logging


logger = logging.getLogger(__name__)

class FileManager:
    
    def __init__(self, base_dir: str = "uploads"):
        self.base_dir = base_dir
        self.raw_dir = f"{base_dir}/raw"
        self.processed_dir = f"{base_dir}/processed"
        self.ensure_directories()
    
    def ensure_directories(self):
        Path(self.raw_dir).mkdir(parents=True, exist_ok=True)
        Path(self.processed_dir).mkdir(parents=True, exist_ok=True)
        Path("output/json").mkdir(parents=True, exist_ok=True)
        Path("output/logs").mkdir(parents=True, exist_ok=True)
    
    def save_upload(self, upload_id: str, file_content: bytes, filename: str) -> str:
        file_path = f"{self.raw_dir}/{upload_id}.pdf"
        try:
            with open(file_path, 'wb') as f:
                f.write(file_content)
            logger.info(f"File saved: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise
    
    def get_upload_path(self, upload_id: str) -> str:
        return f"{self.raw_dir}/{upload_id}.pdf"
    
    def get_processed_dir(self, upload_id: str) -> str:
        processed_path = f"{self.processed_dir}/{upload_id}"
        Path(processed_path).mkdir(parents=True, exist_ok=True)
        return processed_path
    
    def get_result_path(self, upload_id: str) -> str:
        return f"output/json/{upload_id}.json"
    
    def cleanup(self, upload_id: str):
        try:
            raw_file = self.get_upload_path(upload_id)
            processed_dir = f"{self.processed_dir}/{upload_id}"
            
            if os.path.exists(raw_file):
                os.remove(raw_file)
            
            if os.path.exists(processed_dir):
                shutil.rmtree(processed_dir)
            
            logger.info(f"Cleaned up files for {upload_id}")
        except Exception as e:
            logger.error(f"Error cleaning up: {str(e)}")
