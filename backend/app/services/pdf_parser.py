import logging
import os
import re
from typing import Dict, Any, List, Optional

try:
    import PyPDF2
except ImportError:
    logging.error("PyPDF2 not installed. Install it with 'pip install PyPDF2'")

from app.core.parser_interface import FileParserInterface, ParserResult

logger = logging.getLogger(__name__)


class PDFParser(FileParserInterface):
    """
    Parser for PDF files.
    """
    
    def __init__(self):
        """Initialize the PDF parser."""
        # Regex pattern to identify potential section titles
        self.section_pattern = re.compile(r'^(?:\d+[\.\)]\s*)?([A-Z][^\.!?]*?)(?:\.|\:|\n|$)')
        
    def parse(self, file_path: str) -> ParserResult:
        """
        Parse a PDF file and return its structured content.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            A ParserResult object containing the parsed content
        """
        logger.info(f"Parsing PDF file: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            # Ensure PyPDF2 is installed
            if 'PyPDF2' not in globals():
                logger.error("PyPDF2 library not available. Install with 'pip install PyPDF2'")
                raise ImportError("PyPDF2 library not available")
                
            text = self.get_full_text(file_path)
            metadata = self._extract_metadata(file_path)
            sections = self.get_sections(file_path)
            
            return ParserResult(
                text=text,
                sections=sections,
                metadata=metadata,
                file_path=file_path
            )
            
        except Exception as e:
            logger.error(f"Error parsing PDF file {file_path}: {str(e)}")
            raise
    
    def get_full_text(self, file_path: str) -> str:
        """
        Extract the full text content from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            The extracted text content
        """
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text_parts = []
                
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text_parts.append(page.extract_text())
                
                return "\n".join([part for part in text_parts if part.strip()])
                
        except Exception as e:
            logger.error(f"Error extracting text from PDF file {file_path}: {str(e)}")
            raise
    
    def get_sections(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract sections from a PDF file using heuristic methods.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            A list of sections, each containing title and content
        """
        try:
            full_text = self.get_full_text(file_path)
            sections = self._extract_sections(full_text)
                
            # If no sections were found, create a single section with all content
            if not sections:
                sections = [{"title": "Content", "content": full_text}]
                
            return sections
            
        except Exception as e:
            logger.error(f"Error extracting sections from PDF file {file_path}: {str(e)}")
            raise
    
    def _extract_sections(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract sections from the text content using regex patterns.
        
        Args:
            text: The full text content
            
        Returns:
            A list of sections, each containing title and content
        """
        lines = text.split('\n')
        sections = []
        current_section: Optional[Dict[str, Any]] = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if the line looks like a section heading
            match = self.section_pattern.match(line)
            if match and len(line) < 100:  # Avoid matching long paragraphs
                # If we're in a section, save it before starting a new one
                if current_section:
                    current_section["content"] = "\n".join(current_content)
                    sections.append(current_section)
                
                # Start a new section
                current_section = {
                    "title": line.strip(),
                    "content": ""
                }
                current_content = []
            elif current_section is not None:
                # Add to current section content
                current_content.append(line)
            else:
                # This is content before any recognizable section
                # Create an introduction section
                current_section = {
                    "title": "Introduction",
                    "content": ""
                }
                current_content = [line]
        
        # Add the last section
        if current_section:
            current_section["content"] = "\n".join(current_content)
            sections.append(current_section)
            
        return sections
    
    def _extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            A dictionary containing metadata
        """
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                metadata = {
                    "file_size": os.path.getsize(file_path),
                    "page_count": len(reader.pages),
                }
                
                # Extract document information if available
                info = reader.metadata
                if info:
                    if info.get('/Title'):
                        metadata["title"] = info.get('/Title')
                    if info.get('/Author'):
                        metadata["author"] = info.get('/Author')
                    if info.get('/CreationDate'):
                        metadata["created"] = info.get('/CreationDate')
                    if info.get('/ModDate'):
                        metadata["modified"] = info.get('/ModDate')
                    if info.get('/Subject'):
                        metadata["subject"] = info.get('/Subject')
                    if info.get('/Keywords'):
                        metadata["keywords"] = info.get('/Keywords')
                        
                return metadata
                
        except Exception as e:
            logger.warning(f"Error extracting metadata from PDF file {file_path}: {str(e)}")
            # Return basic file metadata if document metadata extraction fails
            return {
                "file_size": os.path.getsize(file_path)
            }
    
    def _count_words(self, text: str) -> int:
        """
        Count the number of words in the text.
        
        Args:
            text: The text to count words in
            
        Returns:
            The word count
        """
        # Split by whitespace and filter out empty strings
        words = [word for word in text.split() if word.strip()]
        return len(words) 