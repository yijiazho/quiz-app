import logging
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from typing import Optional, List, Dict, Any

from app.models.file import UploadedFile
from app.models.parsed_content import ParsedContent

logger = logging.getLogger(__name__)

class FileService:
    """
    Service for handling file operations with the database
    """
    
    @staticmethod
    async def save_file_to_db(
        db: Session, 
        file: UploadFile, 
        file_content: bytes,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> UploadedFile:
        """
        Save an uploaded file to the database.
        
        Args:
            db: Database session
            file: The uploaded file
            file_content: The binary content of the file
            title: Optional title for the file
            description: Optional description for the file
            
        Returns:
            The created UploadedFile object
        """
        try:
            logger.info(f"Saving file to database: {file.filename}")
            
            # Create a new UploadedFile instance
            db_file = UploadedFile(
                filename=file.filename,
                content_type=file.content_type,
                file_size=len(file_content),
                file_content=file_content,
                title=title,
                description=description,
                upload_time=datetime.utcnow()
            )
            
            # Add to database and commit
            db.add(db_file)
            db.commit()
            db.refresh(db_file)
            
            logger.info(f"File saved successfully to database with ID: {db_file.file_id}")
            return db_file
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving file to database: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file to database: {str(e)}"
            )
    
    @staticmethod
    def get_file_by_id(db: Session, file_id: str) -> Optional[UploadedFile]:
        """
        Get a file by its ID.
        
        Args:
            db: Database session
            file_id: ID of the file to retrieve
            
        Returns:
            The file if found, None otherwise
        """
        logger.info(f"Retrieving file with ID: {file_id}")
        
        try:
            file = db.query(UploadedFile).filter(UploadedFile.file_id == file_id).first()
            
            if file:
                # Update last accessed time
                file.last_accessed = datetime.utcnow()
                db.commit()
                logger.info(f"File retrieved successfully: {file.filename}")
            else:
                logger.warning(f"File not found with ID: {file_id}")
                
            return file
            
        except Exception as e:
            logger.error(f"Error retrieving file: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve file: {str(e)}"
            )
    
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