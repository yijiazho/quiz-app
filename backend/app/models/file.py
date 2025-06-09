from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, UTC

from app.core.database import Base

def generate_uuid():
    """Generate a unique identifier for files"""
    return str(uuid.uuid4())

class UploadedFile(Base):
    """Model for storing uploaded files in the database"""
    __tablename__ = "uploaded_files"

    file_id = Column(String, primary_key=True, default=generate_uuid)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    file_content = Column(LargeBinary, nullable=False)  # Stores the binary content of the file
    upload_time = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    last_accessed = Column(DateTime)
    
    # Optional metadata fields for additional information
    title = Column(String)
    description = Column(String)
    
    # Add user relationship
    user_id = Column(String, ForeignKey("users.id"))
    user = relationship("User", back_populates="files")
    
    # Relationship with ParsedContent
    parsed_contents = relationship("ParsedContent", back_populates="file", cascade="all, delete-orphan")
    
    def __repr__(self):
        """String representation of the model"""
        return f"<UploadedFile(file_id='{self.file_id}', filename='{self.filename}')>"
    
    def to_dict(self):
        """Convert model to dictionary (excluding binary content)"""
        return {
            "file_id": self.file_id,
            "filename": self.filename,
            "content_type": self.content_type,
            "file_size": self.file_size,
            "upload_time": self.upload_time.isoformat() if self.upload_time else None,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "title": self.title,
            "description": self.description,
            "parsed_contents": [parsed_content.to_dict() for parsed_content in self.parsed_contents]
        } 