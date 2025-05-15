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
from app.core.cache import cache
import tempfile

from app.core.database import get_db
from app.services.file_service import FileService
from app.schemas.file import FileMetadata, FileUploadResponse, FilesListResponse, ParsedContentResponse
from app.services.parser_factory import ParserFactory
from app.models.parsed_content import ParsedContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Update router prefix to match README specification
router = APIRouter(prefix="/api/upload", tags=["upload"])
file_service = FileService()
parser_factory = ParserFactory()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = FilePath("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.get("/")
@router.get("")  # Handle both with and without trailing slash
async def check_upload_endpoint():
    """
    Simple endpoint to check if the upload router is working.
    """
    logger.info("Checking upload endpoint")
    return {"status": "ok", "message": "Upload endpoint is working"}

@router.post("/")
@router.post("")  # Handle both with and without trailing slash
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a file.
    """
    try:
        # Validate file type
        allowed_types = {
            'application/pdf': '.pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'application/msword': '.doc',
            'text/plain': '.txt'
        }
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_types.keys())}"
            )
        
        # Read file content
        content = await file.read()
        
        # Save to database
        db_file = await file_service.save_file_to_db(
            db=db,
            file=file,
            file_content=content
        )
        
        # Parse the content
        try:
            parser = parser_factory.get_parser(file.content_type)
            # Create a temporary file to parse
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(content)
                temp_file.flush()
                parsed_result = parser.parse(temp_file.name)
            
            # Save parsed content to database
            db_parsed = ParsedContent(
                file_id=db_file.file_id,
                parsed_text=parsed_result.content,
                content_type=file.content_type,
                content_metadata=parsed_result.metadata
            )
            db.add(db_parsed)
            db.commit()
            db.refresh(db_parsed)
            
            logger.info(f"Content parsed and saved successfully for file: {file.filename}")
            parsed_content = db_parsed
        except Exception as parse_error:
            logger.error(f"Error parsing file content: {str(parse_error)}")
            # Don't fail the upload if parsing fails
            parsed_content = None
        
        return {
            "message": "File uploaded and processed successfully",
            "file_id": db_file.file_id,
            "filename": file.filename,
            "parsed": parsed_content is not None
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions without wrapping them
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading file: {str(e)}"
        )

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
    file_id: str,
    db: Session = Depends(get_db)
):
    """
    Download a file by its ID.
    """
    logger.info(f"Downloading file with ID: {file_id}")
    
    try:
        file = file_service.get_file_by_id(db, file_id)
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
            
        # Remove charset from content type if present
        content_type = file.content_type.split(';')[0]
            
        return Response(
            content=file.file_content,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{file.filename}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error downloading file: {str(e)}"
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

@router.get("/parsed-contents")
def list_parsed_contents(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all parsed contents."""
    logger.info("=== Starting parsed-contents request ===")
    logger.info(f"Request parameters - skip: {skip}, limit: {limit}")
    
    try:
        # Query parsed contents
        logger.info("Executing database query...")
        parsed_contents = db.query(ParsedContent).offset(skip).limit(limit).all()
        logger.info(f"Database query returned {len(parsed_contents)} results")
        
        # Log the first few results for debugging
        for i, content in enumerate(parsed_contents[:3]):
            logger.info(f"Content {i + 1}:")
            logger.info(f"  - content_id: {content.content_id}")
            logger.info(f"  - file_id: {content.file_id}")
            logger.info(f"  - content_type: {content.content_type}")
        
        # Convert to dictionaries
        contents = [
            {
                "content_id": content.content_id,
                "file_id": content.file_id,
                "content_type": content.content_type,
                "parsed_text": content.parsed_text,
                "content_metadata": content.content_metadata,
                "parse_time": content.parse_time.isoformat() if content.parse_time else None,
                "last_updated": content.last_updated.isoformat() if content.last_updated else None
            }
            for content in parsed_contents
        ]
        
        response_data = {
            "total": len(contents),
            "contents": contents
        }
        logger.info(f"Preparing response with {len(contents)} contents")
        logger.info("=== Completed parsed-contents request ===")
        
        return response_data
        
    except Exception as e:
        logger.error("=== Error in parsed-contents request ===")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        logger.error("=== End of error log ===")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing parsed contents: {str(e)}"
        ) 