#!/usr/bin/env python3
"""Extract OCR text from image"""

from core.ocr_engine import get_ocr_engine

image_path = "uploads/processed/debug_test/page_1.png"

print("Extracting OCR text...")
print("=" * 80)

try:
    ocr = get_ocr_engine("paddleocr")
    text = ocr.extract_text(image_path)
    
    print(text)
    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
