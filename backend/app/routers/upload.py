from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database_config import get_db
from app.services.file_service import FileService
from app.models.file import UploadedFile
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/upload", tags=["upload"])

@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload a file to the server."""
    try:
        file_service = FileService(db)
        file_record = file_service.save_file(
            file.file,
            file.filename,
            file.content_type,
            title,
            description
        )
        return {
            "file_id": file_record.file_id,
            "filename": file_record.filename,
            "content_type": file_record.content_type,
            "file_size": file_record.file_size,
            "title": file_record.title,
            "description": file_record.description
        }
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
async def list_files(db: Session = Depends(get_db)):
    """List all uploaded files."""
    try:
        file_service = FileService(db)
        files = file_service.list_files()
        return [
            {
                "file_id": file.file_id,
                "filename": file.filename,
                "content_type": file.content_type,
                "file_size": file.file_size,
                "title": file.title,
                "description": file.description,
                "upload_time": file.upload_time,
                "last_accessed": file.last_accessed
            }
            for file in files
        ]
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{file_id}")
async def get_file_metadata(file_id: str, db: Session = Depends(get_db)):
    """Get metadata for a specific file."""
    try:
        file_service = FileService(db)
        file = file_service.get_file(file_id)
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        return {
            "file_id": file.file_id,
            "filename": file.filename,
            "content_type": file.content_type,
            "file_size": file.file_size,
            "title": file.title,
            "description": file.description,
            "upload_time": file.upload_time,
            "last_accessed": file.last_accessed
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{file_id}/download")
async def download_file(file_id: str, db: Session = Depends(get_db)):
    """Download a specific file."""
    try:
        file_service = FileService(db)
        file = file_service.get_file(file_id)
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        return {
            "filename": file.filename,
            "content": file.file_content,
            "content_type": file.content_type
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{file_id}")
async def delete_file(file_id: str, db: Session = Depends(get_db)):
    """Delete a specific file."""
    try:
        file_service = FileService(db)
        if not file_service.delete_file(file_id):
            raise HTTPException(status_code=404, detail="File not found")
        return {"message": "File deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{file_id}")
async def update_file_metadata(
    file_id: str,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Update metadata for a specific file."""
    try:
        file_service = FileService(db)
        file = file_service.update_file_metadata(file_id, title, description)
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        return {
            "file_id": file.file_id,
            "filename": file.filename,
            "content_type": file.content_type,
            "file_size": file.file_size,
            "title": file.title,
            "description": file.description,
            "upload_time": file.upload_time,
            "last_accessed": file.last_accessed
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating file metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 