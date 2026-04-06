from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import Optional
import uuid
import json
from app.api.schemas import UploadResponse, StatusResponse, ErrorResponse
from utils.logger import logger
from core.pipeline import ExtractionPipeline
from utils.file_manager import FileManager

router = APIRouter()

processing_status = {}
file_manager = FileManager()
pipeline = ExtractionPipeline()

@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    try:
        upload_id = str(uuid.uuid4())
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        logger.info(f"File uploaded: {file.filename} with ID: {upload_id}")
        
        if background_tasks:
            background_tasks.add_task(process_document, upload_id, file)
        
        processing_status[upload_id] = {"status": "processing", "upload_id": upload_id, "message": "Analyzing document..."}
        
        return UploadResponse(
            status="processing",
            upload_id=upload_id,
            message="File uploaded successfully. Processing started."
        )
    
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{upload_id}", response_model=StatusResponse)
async def get_status(upload_id: str):
    if upload_id not in processing_status:
        raise HTTPException(status_code=404, detail="Upload ID not found")
    
    return StatusResponse(**processing_status[upload_id])

@router.get("/result/{upload_id}")
async def get_result(upload_id: str):
    if upload_id not in processing_status:
        raise HTTPException(status_code=404, detail="Upload ID not found")
    
    status_info = processing_status[upload_id]
    
    if status_info["status"] != "completed":
        raise HTTPException(status_code=202, detail="Processing not completed yet")
    
    return status_info.get("result")

async def process_document(upload_id: str, file: UploadFile):
    try:
        logger.info(f"Processing document: {upload_id}")
        
        file_content = await file.read()
        file_path = file_manager.save_upload(upload_id, file_content, file.filename)
        
        result = pipeline.process(upload_id, file_path)
        pipeline.save_result(upload_id, result)
        
        processing_status[upload_id] = {
            "status": "completed",
            "upload_id": upload_id,
            "message": "Processing completed",
            "result": result
        }
        
        logger.info(f"Processing completed for {upload_id}")
    
    except Exception as e:
        logger.error(f"Processing error for {upload_id}: {str(e)}")
        processing_status[upload_id] = {
            "status": "failed",
            "upload_id": upload_id,
            "message": f"Processing failed: {str(e)}"
        }
