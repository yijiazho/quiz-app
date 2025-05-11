from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Depends, Path
from fastapi.responses import JSONResponse, Response, StreamingResponse
import os
import logging
from pathlib import Path as FilePath
import traceback
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import io
from datetime import datetime

from app.core.database import get_db
from app.services.file_service import FileService
from app.schemas.file import FileMetadata, FileUploadResponse, FilesListResponse, ParsedContentResponse
from app.services.parser import ParserFactory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["upload"])
file_service = FileService()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = FilePath("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.get("/")
async def check_upload_endpoint():
    """
    Simple endpoint to check if the upload router is working.
    """
    return {"status": "ok", "message": "Upload endpoint is working"}

@router.post("/file", response_model=ParsedContentResponse)
async def upload_file(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Upload and parse a file."""
    try:
        # Save the file temporarily
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        try:
            # Get the appropriate parser
            parser = ParserFactory.get_parser(file_path)
            if not parser:
                raise HTTPException(status_code=400, detail="Unsupported file type")

            # Parse the file
            result = parser.parse()
            return result.dict()
        finally:
            # Clean up the temporary file
            if os.path.exists(file_path):
                os.remove(file_path)
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files", response_model=FilesListResponse)
def list_files(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all uploaded files with metadata."""
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
    """Get metadata for a specific file."""
    logger.info(f"Getting metadata for file with ID: {file_id}")
    return FileService.get_file_metadata(db, file_id)

@router.get("/files/{file_id}/download")
def download_file(
    file_id: str = Path(..., description="The unique identifier of the file"),
    db: Session = Depends(get_db)
):
    """Download a file from the database."""
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
    """Delete a file from the database."""
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