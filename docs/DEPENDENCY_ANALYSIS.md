# 📦 Dependency Analysis & Docker Deployment Issues

## 🔴 Current Installation Issues

### Issue 1: PyMuPDF (pymupdf)
**Problem**: 
- Version 1.23.8 doesn't exist
- Requires Visual Studio C++ compiler on Windows
- Needs build tools

**Solution**:
- Use latest version: `pymupdf==1.27.2.2`
- Or use pre-built wheels: `pip install --only-binary :all: pymupdf`

**Docker Impact**: ⚠️ MAJOR
- Docker image will need: `build-essential`, `gcc`, `g++`
- Image size increases significantly
- Build time increases

---

### Issue 2: PaddleOCR
**Problem**:
- Large download (~200MB+ models)
- Requires numpy, opencv
- First run downloads models

**Solution**:
- Install: `pip install paddleocr`
- Pre-download models in Docker

**Docker Impact**: ⚠️ MAJOR
- Image size: +500MB-1GB
- Build time: 5-10 minutes
- Runtime: Models cached in container

---

### Issue 3: EasyOCR
**Problem**:
- Also large (~300MB+ models)
- Requires torch (PyTorch)
- Heavy dependencies

**Solution**:
- Install: `pip install easyocr`
- Pre-download models

**Docker Impact**: ⚠️ CRITICAL
- Image size: +1GB-2GB
- PyTorch alone: 500MB+
- Build time: 10-15 minutes

---

### Issue 4: Tesseract
**Problem**:
- Requires system package installation
- Not in pip

**Solution**:
- Windows: Download from GitHub
- Linux: `apt-get install tesseract-ocr`
- Mac: `brew install tesseract`

**Docker Impact**: ✅ MINOR
- Just system package
- Image size: +50MB
- Build time: <1 minute

---

### Issue 5: OpenCV (opencv-python)
**Problem**:
- Large binary (~100MB)
- Requires system libraries

**Solution**:
- Install: `pip install opencv-python`

**Docker Impact**: ⚠️ MEDIUM
- Image size: +150MB
- Requires: libsm6, libxext6, libxrender-dev

---

## 📊 Pip Installation Strategy

### Recommended Approach:

**Option A: Lightweight (Tesseract Only)**
```
fastapi
uvicorn
pydantic
pydantic-settings
pytesseract
python-multipart
python-dotenv
pyyaml
aiofiles
```
**Size**: ~200MB
**Time**: 2-3 minutes

**Option B: Balanced (PaddleOCR)**
```
fastapi
uvicorn
pydantic
pydantic-settings
paddleocr
pymupdf
numpy
opencv-python
python-multipart
python-dotenv
pyyaml
aiofiles
```
**Size**: ~800MB-1GB
**Time**: 5-8 minutes

**Option C: Full (All OCR Engines)**
```
fastapi
uvicorn
pydantic
pydantic-settings
paddleocr
easyocr
pytesseract
pymupdf
numpy
opencv-python
torch
python-multipart
python-dotenv
pyyaml
aiofiles
```
**Size**: ~2GB-3GB
**Time**: 15-20 minutes

---

## 🐳 Docker Deployment Issues

### Issue 1: Image Size
**Current**: 2-3GB (with all OCR engines)
**Problem**: 
- Slow deployment
- High bandwidth usage
- Expensive storage

**Solution**:
- Use multi-stage builds
- Only include needed OCR engine
- Use slim base image

---

### Issue 2: Build Time
**Current**: 15-20 minutes
**Problem**:
- Slow CI/CD pipeline
- Expensive compute
- Development friction

**Solution**:
- Cache pip packages
- Pre-build base image
- Use layer caching

---

### Issue 3: System Dependencies
**Required for Docker**:
```dockerfile
# For PyMuPDF
RUN apt-get install -y build-essential gcc g++

# For OpenCV
RUN apt-get install -y libsm6 libxext6 libxrender-dev

# For Tesseract
RUN apt-get install -y tesseract-ocr

# For PaddleOCR/EasyOCR
RUN apt-get install -y libgomp1
```

---

### Issue 4: Model Downloads
**Problem**:
- Models downloaded at runtime
- Takes 5-10 minutes on first run
- Network dependent

**Solution**:
- Pre-download in Docker build
- Cache in volume
- Use environment variables

---

## 📋 Recommended Docker Setup

### Dockerfile Strategy:

```dockerfile
# Stage 1: Base
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libsm6 \
    libxext6 \
    libxrender-dev \
    tesseract-ocr \
    libgomp1

# Stage 2: Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Pre-download OCR models
RUN python -c "from paddleocr import PaddleOCR; PaddleOCR()"

# Stage 4: Application
COPY . .
CMD ["python", "-m", "app.main"]
```

**Result**:
- Image size: ~1.5GB
- Build time: 10-12 minutes
- Runtime: <1 second startup

---

## ✅ Current Pip Installation Issues (Windows)

### 1. PyMuPDF
```
ERROR: Could not find a version that satisfies the requirement pymupdf==1.23.8
```
**Fix**: Use `pymupdf==1.27.2.2`

### 2. Visual Studio Not Found
```
Exception: Unable to find Visual Studio
```
**Fix**: 
- Install Visual Studio Build Tools
- Or use: `pip install --only-binary :all: pymupdf`

### 3. Missing System Libraries
```
ImportError: libsm6 not found
```
**Fix**: Only on Linux/Docker, not Windows

---

## 🎯 Immediate Action Items

### For Local Development (Windows):
1. ✅ Use `pymupdf==1.27.2.2`
2. ✅ Install with pre-built wheels: `pip install --only-binary :all: pymupdf`
3. ✅ Skip EasyOCR (too heavy)
4. ✅ Use PaddleOCR or Tesseract

### For Docker Deployment:
1. ⚠️ Use multi-stage builds
2. ⚠️ Pre-download OCR models
3. ⚠️ Install system dependencies
4. ⚠️ Use slim base image
5. ⚠️ Cache pip packages

---

## 📊 Comparison Table

| Component | Local (Windows) | Docker | Issue |
|-----------|-----------------|--------|-------|
| PyMuPDF | ⚠️ Needs VS | ✅ Easy | Build tools |
| PaddleOCR | ✅ Works | ⚠️ 500MB | Size |
| EasyOCR | ⚠️ Heavy | ❌ 1GB+ | PyTorch |
| Tesseract | ✅ Works | ✅ Easy | System pkg |
| OpenCV | ✅ Works | ⚠️ Libs needed | System libs |

---

## 🚀 Recommended Setup

### For Now (Local):
```
fastapi
uvicorn
pydantic
pydantic-settings
paddleocr
pymupdf==1.27.2.2
numpy
opencv-python
python-multipart
python-dotenv
pyyaml
aiofiles
```

### For Docker:
```
fastapi
uvicorn
pydantic
pydantic-settings
paddleocr
pymupdf==1.27.2.2
numpy
opencv-python
python-multipart
python-dotenv
pyyaml
aiofiles
```

**Same packages, but Docker handles system dependencies**

---

## ⚠️ Docker Deployment Challenges

1. **Image Size**: 1-2GB (acceptable)
2. **Build Time**: 10-15 minutes (acceptable)
3. **Model Download**: 5-10 minutes first run (acceptable)
4. **System Dependencies**: Need apt-get (manageable)
5. **GPU Support**: Optional, not required for CPU

---

## ✅ Summary

### Current Issues:
- ❌ PyMuPDF version mismatch
- ❌ Visual Studio not installed
- ⚠️ Large dependencies (OCR models)

### Solutions:
- ✅ Update to `pymupdf==1.27.2.2`
- ✅ Use pre-built wheels
- ✅ Docker handles system dependencies

### Docker Readiness:
- ⚠️ Image will be 1-2GB
- ⚠️ Build time 10-15 minutes
- ✅ Runtime performance good
- ✅ All dependencies manageable

**No blocking issues for Docker deployment!**
