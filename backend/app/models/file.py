from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, Text
from sqlalchemy.sql import func
import uuid
from datetime import datetime

from app.core.database import Base

def generate_uuid():
    """Generate a unique identifier for files"""
    return str(uuid.uuid4())

class UploadedFile(Base):
    """Model for storing uploaded files in the database"""
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, unique=True, index=True, default=generate_uuid)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    file_content = Column(LargeBinary, nullable=False)  # Stores the binary content of the file
    upload_time = Column(DateTime, default=func.now())
    last_accessed = Column(DateTime, nullable=True)
    
    # Optional metadata fields for additional information
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    
    def __repr__(self):
        """String representation of the model"""
        return f"<UploadedFile(id={self.id}, filename={self.filename}, size={self.file_size})>"
    
    def to_dict(self):
        """Convert model to dictionary (excluding binary content)"""
        return {
            "id": self.id,
            "file_id": self.file_id,
            "filename": self.filename,
            "content_type": self.content_type,
            "file_size": self.file_size,
            "upload_time": self.upload_time.isoformat() if self.upload_time else None,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "title": self.title,
            "description": self.description
        } 