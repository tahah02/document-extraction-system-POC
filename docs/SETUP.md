# Setup Guide

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation Steps

### 1. Clone or Extract Project

```bash
cd document-extraction-poc
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
```

### 5. Create Required Directories

```bash
mkdir -p uploads/raw uploads/processed
mkdir -p output/json output/logs
mkdir -p temp
```

### 6. Run Application

```bash
python -m app.main
```

The API will be available at: `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## OCR Engine Selection

### PaddleOCR (Recommended for CPU)
- Best accuracy on CPU
- Supports multiple languages
- Slower but more accurate

```bash
pip install paddleocr
```

### EasyOCR
- Good balance of speed and accuracy
- Supports 80+ languages

```bash
pip install easyocr
```

### Tesseract
- Lightweight and fast
- Requires system installation

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

## Configuration

### OCR Settings (`config/ocr_config.json`)

```json
{
  "engine": "paddleocr",
  "language": "en",
  "confidence_threshold": 0.5,
  "use_gpu": false
}
```

### Extraction Config (`config/extraction_config.json`)

Define field keywords and patterns for extraction.

## Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=core tests/
```

## Troubleshooting

### PaddleOCR Download Issues
- First run downloads models (~200MB)
- Set environment variable: `PADDLEOCR_HOME=/path/to/cache`

### Memory Issues
- Reduce image zoom factor in `config/ocr_config.json`
- Process documents one at a time

### Slow Processing
- Use Tesseract for faster (but less accurate) results
- Reduce image DPI in configuration

## Production Deployment

For production, consider:
1. Using a process manager (Gunicorn, Supervisor)
2. Setting up a database for results storage
3. Implementing authentication/authorization
4. Using a reverse proxy (Nginx)
5. Setting up monitoring and logging

Example with Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
```
