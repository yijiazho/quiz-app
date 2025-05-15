import logging
import os
import re
from typing import Dict, Any, List, Optional
import io

try:
    import PyPDF2
except ImportError:
    logging.error("PyPDF2 not installed. Install it with 'pip install PyPDF2'")

from app.core.parser_interface import FileParserInterface, ParserResult
from .parser_interface import ParserInterface

logger = logging.getLogger(__name__)


class PDFParser(ParserInterface):
    """Parser for PDF files"""
    
    def supports_content_type(self, content_type: str) -> bool:
        """Check if this parser supports PDF content type"""
        return content_type.lower() in ['application/pdf', 'pdf']
    
    async def parse(self, content: bytes) -> Dict[str, Any]:
        """
        Parse PDF content and extract text and metadata
        
        Args:
            content: The binary content of the PDF file
            
        Returns:
            Dict containing:
                - parsed_text: The extracted text content
                - metadata: Additional metadata about the PDF
        """
        try:
            # Create a PDF reader object
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract text from each page
            text_content = []
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_content.append(page.extract_text())
            
            # Get PDF metadata
            metadata = {
                "num_pages": len(pdf_reader.pages),
                "title": pdf_reader.metadata.get('/Title', ''),
                "author": pdf_reader.metadata.get('/Author', ''),
                "creation_date": pdf_reader.metadata.get('/CreationDate', ''),
                "modification_date": pdf_reader.metadata.get('/ModDate', '')
            }
            
            return {
                "parsed_text": "\n\n".join(text_content),
                "metadata": metadata
            }
            
        except Exception as e:
            raise ValueError(f"Error parsing PDF: {str(e)}")

class PDFParser(FileParserInterface):
    """
    Parser for PDF files.
    """
    
    def __init__(self):
        """Initialize the PDF parser."""
        # Regex pattern to identify potential section titles
        self.section_pattern = re.compile(r'^(?:\d+[\.\)]\s*)?([A-Z][^\.!?]*?)(?:\.|\:|\n|$)')
        
    def supports_content_type(self, content_type: str) -> bool:
        """
        Check if this parser supports the given content type.
        
        Args:
            content_type: The MIME type to check
            
        Returns:
            True if this parser supports the content type, False otherwise
        """
        return content_type.lower() == 'application/pdf'
        
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
            sections = self.get_sections(text)
            
            # If no sections were found, create a single section with all content
            if not sections:
                sections = [{"title": "Content", "content": text}]
                
            return ParserResult(
                title=metadata.get('title', os.path.basename(file_path)),
                content=text,
                sections=sections,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error parsing PDF file {file_path}: {str(e)}")
            raise
    
    def get_full_text(self, file_path: str) -> str:
        """
        Get the full text content of a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            The full text content of the file
        """
        logger.info(f"Getting full text from PDF file: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
                
        except Exception as e:
            logger.error(f"Error reading PDF file {file_path}: {str(e)}")
            raise
    
    def get_sections(self, text: str) -> List[Dict[str, Any]]:
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