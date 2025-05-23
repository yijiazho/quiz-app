from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class ParserResult:
    """Result from parsing a file"""
    title: str = ""
    content: str = ""
    sections: Dict[str, str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize default values for optional fields"""
        if self.sections is None:
            self.sections = {}
        if self.metadata is None:
            self.metadata = {}

class ParserInterface(ABC):
    """Interface for file parsers"""
    
    @abstractmethod
    async def parse(self, content: bytes) -> Dict[str, Any]:
        """
        Parse the file content and return the extracted text and metadata
        
        Args:
            content: The binary content of the file
            
        Returns:
            Dict containing:
                - parsed_text: The extracted text content
                - metadata: Additional metadata about the parsed content
        """
        pass
    
    @abstractmethod
    def supports_content_type(self, content_type: str) -> bool:
        """
        Check if this parser supports the given content type
        
        Args:
            content_type: The MIME type of the file
            
        Returns:
            True if this parser can handle the content type, False otherwise
        """
        pass

class FileParserInterface(ABC):
    """Interface for file parsers"""
    
    @abstractmethod
    def parse(self, filepath: str) -> ParserResult:
        """
        Parse the given file and return a ParserResult
        
        Args:
            filepath: Path to the file to parse
            
        Returns:
            ParserResult containing the parsed content, sections and metadata
        """
        pass
    
    @abstractmethod
    def get_full_text(self, filepath: str) -> str:
        """
        Get the full text content of the file
        
        Args:
            filepath: Path to the file
            
        Returns:
            String containing the full text content
        """
        pass
    
    @abstractmethod
    def get_sections(self, filepath: str) -> Dict[str, str]:
        """
        Get sections from the file
        
        Args:
            filepath: Path to the file
            
        Returns:
            Dictionary mapping section names to their content
        """
        pass 