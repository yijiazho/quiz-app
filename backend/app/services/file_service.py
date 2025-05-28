import os
import uuid
from datetime import datetime, UTC
from typing import Optional, BinaryIO
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from typing import List, Dict, Any

from app.models.file import UploadedFile
from app.models.parsed_content import ParsedContent
from app.core.database_config import get_db
import logging

logger = logging.getLogger(__name__)

class FileService:
    """
    Service for handling file operations with the database
    """
    
    def __init__(self, db: Session):
        self.db = db

    def save_file(self, file: BinaryIO, filename: str, content_type: str, title: Optional[str] = None, description: Optional[str] = None) -> UploadedFile:
        """Save a file to the database."""
        try:
            logger.info(f"Saving file to database: {filename}")
            logger.info(f"Received metadata - title: {title}, description: {description}")
            
            # Validate title length
            if title and len(title) > 1000:
                raise HTTPException(status_code=422, detail="Title must be at most 1000 characters long")
            
            # Read file content
            file_content = file.read()
            file_size = len(file_content)
            
            # Create file record
            file_record = UploadedFile(
                file_id=str(uuid.uuid4()),
                filename=filename,
                content_type=content_type,
                file_size=file_size,
                file_content=file_content,
                upload_time=datetime.now(UTC),
                title=title,
                description=description
            )
            
            # Save to database
            self.db.add(file_record)
            self.db.commit()
            self.db.refresh(file_record)
            
            logger.info(f"File saved successfully: {filename}")
            logger.info(f"Saved metadata - title: {file_record.title}, description: {file_record.description}")
            return file_record
            
        except Exception as e:
            import traceback
            logger.error(f"Error saving file to database: {str(e)}\n{traceback.format_exc()}")
            self.db.rollback()
            raise

    def get_file(self, file_id: str) -> Optional[UploadedFile]:
        """Get a file from the database."""
        try:
            file = self.db.query(UploadedFile).filter(UploadedFile.file_id == file_id).first()
            if file:
                file.last_accessed = datetime.now(UTC)
                self.db.commit()
            return file
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error getting file from database: {str(e)}")
            raise

    def list_files(self) -> list[UploadedFile]:
        """List all files in the database."""
        try:
            return self.db.query(UploadedFile).all()
        except Exception as e:
            logger.error(f"Error listing files from database: {str(e)}")
            raise

    def delete_file(self, file_id: str) -> bool:
        """Delete a file from the database."""
        try:
            file = self.db.query(UploadedFile).filter(UploadedFile.file_id == file_id).first()
            if file:
                self.db.delete(file)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting file from database: {str(e)}")
            raise

    def update_file_metadata(self, file_id: str, title: Optional[str] = None, description: Optional[str] = None) -> Optional[UploadedFile]:
        """Update file metadata."""
        try:
            file = self.db.query(UploadedFile).filter(UploadedFile.file_id == file_id).first()
            if file:
                if title is not None:
                    file.title = title
                if description is not None:
                    file.description = description
                self.db.commit()
                self.db.refresh(file)
            return file
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating file metadata: {str(e)}")
            raise

    @staticmethod
    def get_file_metadata(db: Session, file_id: str) -> Dict[str, Any]:
        """
        Get metadata for a file without fetching the binary content.
        
        Args:
            db: Database session
            file_id: The unique identifier of the file
            
        Returns:
            The file metadata as a dictionary
        """
        db_file = FileService.get_file_by_id(db, file_id)
        
        if not db_file:
            raise HTTPException(
                status_code=404,
                detail=f"File with ID {file_id} not found"
            )
            
        return db_file.to_dict()
    
    @staticmethod
    def list_files(db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List all files in the database (without binary content).
        
        Args:
            db: Database session
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            A list of file metadata dictionaries
        """
        try:
            logger.info(f"Listing files from database (skip={skip}, limit={limit})")
            
            # Query the database for files
            db_files = db.query(UploadedFile).offset(skip).limit(limit).all()
            
            # Convert to dictionaries (excluding binary content)
            result = [file.to_dict() for file in db_files]
            
            logger.info(f"Retrieved {len(result)} files from database")
            return result
            
        except Exception as e:
            logger.error(f"Error listing files from database: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list files from database: {str(e)}"
            )
    
    @staticmethod
    def delete_file(db: Session, file_id: str) -> bool:
        """
        Delete a file from the database.
        
        Args:
            db: Database session
            file_id: ID of the file to delete
            
        Returns:
            True if the file was deleted successfully, False otherwise
        """
        logger.info(f"Deleting file with ID: {file_id}")
        
        try:
            # Get the file
            file = FileService.get_file_by_id(db, file_id)
            if not file:
                logger.warning(f"File not found: {file_id}")
                return False
                
            # Delete parsed content first
            parsed_content = db.query(ParsedContent).filter(ParsedContent.file_id == file_id).first()
            if parsed_content:
                db.delete(parsed_content)
                db.commit()
                
            # Delete the file
            db.delete(file)
            db.commit()
            
            logger.info(f"File deleted successfully: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file from database: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete file: {str(e)}"
            )

    @staticmethod
    def get_file_by_id(db: Session, file_id: str) -> Optional[UploadedFile]:
        """
        Retrieve a file by its ID using the provided database session.
        """
        return db.query(UploadedFile).filter(UploadedFile.file_id == file_id).first() 