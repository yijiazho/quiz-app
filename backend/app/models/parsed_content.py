from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base

def generate_uuid():
    """Generate a unique identifier for parsed content"""
    return str(uuid.uuid4())

class ParsedContent(Base):
    """Model for storing parsed content from uploaded files"""
    __tablename__ = "parsed_contents"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(String, unique=True, index=True, default=generate_uuid)
    file_id = Column(String, ForeignKey("uploaded_files.file_id"), nullable=False)
    content_type = Column(String, nullable=False)  # 'pdf', 'text', etc.
    parsed_text = Column(Text, nullable=False)  # The extracted text content
    content_metadata = Column(JSON, nullable=True)  # Additional metadata like page numbers, sections, etc.
    parse_time = Column(DateTime, default=func.now())
    last_updated = Column(DateTime, onupdate=func.now())
    
    # Relationship with UploadedFile
    file = relationship("UploadedFile", back_populates="parsed_content")
    
    def __repr__(self):
        """String representation of the model"""
        return f"<ParsedContent(id={self.id}, file_id={self.file_id}, content_type={self.content_type})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "content_id": self.content_id,
            "file_id": self.file_id,
            "content_type": self.content_type,
            "parsed_text": self.parsed_text,
            "metadata": self.content_metadata,
            "parse_time": self.parse_time.isoformat() if self.parse_time else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        } 