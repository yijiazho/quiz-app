from typing import Dict, Any, List, Optional
from .parser_interface import ParserInterface, ParserResult
import re
import os
import logging
from app.core.parser_interface import FileParserInterface, ParserResult

logger = logging.getLogger(__name__)

class TextParser(FileParserInterface):
    """
    Parser for text files.
    """
    
    def __init__(self):
        """Initialize the text parser."""
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
        return content_type.lower() == 'text/plain'
    
    def parse(self, file_path: str) -> ParserResult:
        """
        Parse a text file and return its structured content.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            A ParserResult object containing the parsed content
        """
        logger.info(f"Parsing text file: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                
            sections = self.get_sections(text)
            
            # If no sections were found, create a single section with all content
            if not sections:
                sections = [{"title": "Content", "content": text}]
                
            return ParserResult(
                title=os.path.basename(file_path),
                content=text,
                sections=sections,
                metadata={
                    "file_size": os.path.getsize(file_path),
                    "encoding": "utf-8"
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing text file {file_path}: {str(e)}")
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

    def get_full_text(self, file_path: str) -> str:
        """
        Get the full text content of a file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            The full text content of the file
        """
        logger.info(f"Getting full text from file: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
            
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {str(e)}")
            raise 