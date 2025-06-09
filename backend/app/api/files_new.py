from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import logging
from typing import List, Dict, Any
from datetime import datetime

from app.core.database_config import get_db
from app.models.parsed_content import ParsedContent
from app.models.file import UploadedFile
from app.services.file_service import FileService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/files", tags=["files"])

@router.get("/")
async def list_files(db: Session = Depends(get_db)):
    """List all uploaded files."""
    logger.info("=== Starting files list request ===")
    
    try:
        # Query all uploaded files
        logger.info("Executing database query...")
        files = db.query(UploadedFile).all()
        logger.info(f"Database query returned {len(files)} results")
        
        # Convert to response format
        files_list = [
            {
                "file_id": file.file_id,
                "filename": file.filename,
                "content_type": file.content_type,
                "file_size": file.file_size,
                "upload_time": file.upload_time.isoformat() if file.upload_time else None,
                "last_accessed": file.last_accessed.isoformat() if file.last_accessed else None,
                "title": file.title,
                "description": file.description,
                "is_parsed": len(file.parsed_contents) > 0,
                "parsed_contents_count": len(file.parsed_contents)
            }
            for file in files
        ]
        
        response_data = {
            "total": len(files_list),
            "files": files_list
        }
        
        logger.info(f"Preparing response with {len(files_list)} files")
        logger.info("=== Completed files list request ===")
        
        return response_data
        
    except Exception as e:
        logger.error("=== Error in files list request ===")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error("=== End of error log ===")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing files: {str(e)}"
        )

@router.get("/{file_id}")
async def get_file(file_id: str, db: Session = Depends(get_db)):
    """Get file metadata."""
    logger.info(f"Getting file metadata for ID: {file_id}")
    
    try:
        file = FileService.get_file_by_id(db, file_id)
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
            
        return file.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file metadata: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting file metadata: {str(e)}"
        )

@router.get("/{file_id}/content")
async def get_file_content(file_id: str, db: Session = Depends(get_db)):
    """Get parsed file content."""
    logger.info(f"Getting file content for ID: {file_id}")
    
    try:
        # Get the parsed content
        parsed_content = db.query(ParsedContent).filter(ParsedContent.file_id == file_id).first()
        if not parsed_content:
            raise HTTPException(status_code=404, detail="File content not found")
            
        return {
            "file_id": parsed_content.file_id,
            "content_type": parsed_content.content_type,
            "parsed_text": parsed_content.parsed_text,
            "content_metadata": parsed_content.content_metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file content: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting file content: {str(e)}"
        )

@router.delete("/{file_id}")
async def delete_file(file_id: str, db: Session = Depends(get_db)):
    """Delete a file."""
    logger.info(f"Deleting file with ID: {file_id}")
    
    try:
        success = FileService.delete_file(db, file_id)
        if not success:
            raise HTTPException(status_code=404, detail="File not found")
            
        return {"message": "File deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting file: {str(e)}"
        ) 