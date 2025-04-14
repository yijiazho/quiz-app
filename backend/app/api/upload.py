from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Depends, Path
from fastapi.responses import JSONResponse, Response, StreamingResponse
import os
import logging
from pathlib import Path as FilePath
import traceback
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import io

from app.core.database import get_db
from app.services.file_service import FileService
from app.schemas.file import FileMetadata, FileUploadResponse, FilesListResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = FilePath("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.get("/")
async def check_upload_endpoint():
    """
    Simple endpoint to check if the upload router is working.
    """
    return {"status": "ok", "message": "Upload endpoint is working"}

@router.post("/", response_model=FileUploadResponse, status_code=201)
async def upload_file(
    request: Request, 
    file: UploadFile = File(...),
    title: Optional[str] = None,
    description: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Upload a file (PDF, DOCX, TXT) for quiz generation.
    The file is stored in the database.
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
        
        if file_extension not in ['.pdf', '.docx', '.doc', '.txt', '.json']:
            logger.warning(f"Invalid file type: {file_extension}")
            raise HTTPException(
                status_code=400,
                detail="Only PDF, DOCX, TXT, and JSON files are allowed"
            )
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        logger.info(f"File size: {file_size} bytes")
        
        # Validate file size (max 10MB)
        if file_size > 10 * 1024 * 1024:  # 10MB
            logger.warning(f"File too large: {file_size} bytes")
            raise HTTPException(
                status_code=400,
                detail="File size should be less than 10MB"
            )
        
        # Reset file position for further operations if needed
        await file.seek(0)
        
        # Save file to database
        db_file = await FileService.save_file_to_db(
            db=db,
            file=file,
            file_content=file_content,
            title=title,
            description=description
        )
        
        # Return response with file metadata
        return {
            "message": "File uploaded successfully",
            "file_id": db_file.file_id,
            "filename": db_file.filename,
            "content_type": db_file.content_type,
            "file_size": db_file.file_size,
            "upload_time": db_file.upload_time.isoformat() if db_file.upload_time else None,
        }
        
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

@router.get("/files", response_model=FilesListResponse)
def list_files(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all uploaded files with metadata (without binary content).
    
    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        A list of file metadata
    """
    logger.info(f"Listing files with pagination (skip={skip}, limit={limit})")
    files = FileService.list_files(db, skip, limit)
    return {
        "total": len(files),
        "files": files
    }

@router.get("/files/{file_id}", response_model=FileMetadata)
def get_file_metadata(
    file_id: str = Path(..., description="The unique identifier of the file"),
    db: Session = Depends(get_db)
):
    """
    Get metadata for a specific file without downloading the content.
    
    Args:
        file_id: The unique identifier of the file
        db: Database session
        
    Returns:
        The file metadata
    """
    logger.info(f"Getting metadata for file with ID: {file_id}")
    return FileService.get_file_metadata(db, file_id)

@router.get("/files/{file_id}/download")
def download_file(
    file_id: str = Path(..., description="The unique identifier of the file"),
    db: Session = Depends(get_db)
):
    """
    Download a file from the database.
    
    Args:
        file_id: The unique identifier of the file
        db: Database session
        
    Returns:
        The file content as a streaming response
    """
    logger.info(f"Downloading file with ID: {file_id}")
    
    # Get the file from the database
    db_file = FileService.get_file_by_id(db, file_id)
    
    if not db_file:
        logger.warning(f"File with ID {file_id} not found for download")
        raise HTTPException(
            status_code=404,
            detail=f"File with ID {file_id} not found"
        )
    
    # Create a BytesIO object from the file content
    file_stream = io.BytesIO(db_file.file_content)
    
    # Return the file as a streaming response
    return StreamingResponse(
        file_stream,
        media_type=db_file.content_type,
        headers={
            "Content-Disposition": f"attachment; filename={db_file.filename}"
        }
    )

@router.delete("/files/{file_id}")
def delete_file(
    file_id: str = Path(..., description="The unique identifier of the file"),
    db: Session = Depends(get_db)
):
    """
    Delete a file from the database.
    
    Args:
        file_id: The unique identifier of the file
        db: Database session
        
    Returns:
        A success message
    """
    logger.info(f"Deleting file with ID: {file_id}")
    
    # Delete the file from the database
    success = FileService.delete_file(db, file_id)
    
    if not success:
        logger.warning(f"File with ID {file_id} not found for deletion")
        raise HTTPException(
            status_code=404,
            detail=f"File with ID {file_id} not found"
        )
    
    return JSONResponse(
        content={
            "message": f"File with ID {file_id} deleted successfully"
        },
        status_code=200
    ) 