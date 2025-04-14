from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
import os
import shutil
import logging
from pathlib import Path
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.get("/")
async def check_upload_endpoint():
    """
    Simple endpoint to check if the upload router is working.
    """
    return {"status": "ok", "message": "Upload endpoint is working"}

@router.post("/")
async def upload_file(request: Request, file: UploadFile = File(...)):
    """
    Upload a file (PDF or DOCX) for quiz generation.
    """
    try:
        logger.info(f"Received upload request for file: {file.filename}")
        logger.info(f"Client host: {request.client.host}")
        
        # Log headers for debugging
        logger.info("Request headers:")
        for name, value in request.headers.items():
            logger.info(f"  {name}: {value}")
            
        # Validate file type
        file_extension = os.path.splitext(file.filename)[1].lower()
        logger.info(f"File extension: {file_extension}")
        
        if file_extension not in ['.pdf', '.docx', '.doc', '.txt']:
            logger.warning(f"Invalid file type: {file_extension}")
            raise HTTPException(
                status_code=400,
                detail="Only PDF, DOCX, and TXT files are allowed"
            )
        
        # Validate file size (max 10MB)
        file_size = 0
        chunk_size = 1024 * 1024  # 1MB chunks
        
        # Read file in chunks to check size
        file_content = await file.read()
        file_size = len(file_content)
        
        logger.info(f"File size: {file_size} bytes")
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            logger.warning(f"File too large: {file_size} bytes")
            raise HTTPException(
                status_code=400,
                detail="File size should be less than 10MB"
            )
        
        # Reset file content
        await file.seek(0)
        
        # Save file
        file_path = UPLOAD_DIR / file.filename
        logger.info(f"Saving file to: {file_path}")
        
        try:
            with open(file_path, "wb") as buffer:
                buffer.write(file_content)
                
            logger.info(f"File saved successfully: {file_path}")
        except Exception as e:
            logger.error(f"Failed to save file: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file: {str(e)}"
            )
        
        # TODO: Process file for quiz generation
        # This will be implemented in future tickets
        
        return JSONResponse(
            content={
                "message": "File uploaded successfully",
                "filename": file.filename,
                "file_path": str(file_path),
                "file_size": file_size,
                "file_type": file_extension
            },
            status_code=201
        )
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        ) 