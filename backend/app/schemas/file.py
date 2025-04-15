from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any

class FileMetadata(BaseModel):
    """Schema for file metadata response"""
    id: int
    file_id: str
    filename: str
    content_type: str
    file_size: int
    upload_time: datetime
    last_accessed: Optional[datetime] = None
    title: Optional[str] = None
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

class FileUploadResponse(BaseModel):
    """Schema for file upload response"""
    message: str = Field(..., example="File uploaded successfully")
    file_id: str = Field(..., example="123e4567-e89b-12d3-a456-426614174000")
    filename: str = Field(..., example="document.pdf")
    content_type: str = Field(..., example="application/pdf")
    file_size: int = Field(..., example=1024)
    upload_time: str = Field(..., example="2023-01-01T12:00:00")

class FilesListResponse(BaseModel):
    """Schema for listing files"""
    total: int
    files: List[FileMetadata]

class ParsedContentResponse(BaseModel):
    """
    Schema for parsed file content response.
    """
    file_id: str
    filename: str
    title: Optional[str] = None
    content: str
    sections: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}
    parsed_at: datetime 