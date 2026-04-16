import os
import sys
import sys


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['PADDLE_DEVICE'] = 'cpu'
os.environ['PADDLE_DISABLE_ONEDNN'] = '1'
os.environ['PADDLE_DISABLE_FAST_MATH'] = '1'
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

try:
    import pytesseract
    pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
except:
    pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.config import settings
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Document Extraction System",
    description="Extract structured data from Pay Slips and Bank Statements",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
