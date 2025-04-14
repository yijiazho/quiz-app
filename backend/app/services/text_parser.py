import os
import re
from typing import List, Dict, Any, Optional
import logging

from app.core.parser_interface import FileParserInterface, ParserResult

logger = logging.getLogger(__name__)


class TextParser(FileParserInterface):
    """
    Parser for plain text files (.txt).
    Attempts to identify sections based on common heading patterns.
    """

    def __init__(self):
        # Regex patterns for identifying headings
        self.heading_patterns = [
            # Chapter/Section with numbers (e.g., "Chapter 1:", "Section 2.1")
            r"^(?:Chapter|Section|CHAPTER|SECTION)\s+\d+(?:\.\d+)*\s*(?:[:.-])?\s*(.*?)$",
            
            # Numbered items (e.g., "1.", "1.1", "I.", "A.")
            r"^(?:\d+|\([a-zA-Z0-9]+\)|[IVXLCDM]+|\([IVXLCDM]+\)|[A-Z])(?:\.\d+)*\s*(?:[:.-])?\s*(.*?)$",
            
            # All caps lines that might be headings
            r"^([A-Z][A-Z\s]{4,})$",
            
            # Lines with trailing underscores or equal signs
            r"^(.*?)\s*[_=]+\s*$",
        ]

    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a text file and extract its content as structured text.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            A dictionary with the structured content
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Extract title from filename if no explicit title is found
        filename = os.path.basename(file_path)
        title = os.path.splitext(filename)[0]
        
        # Get full text
        full_text = self.get_full_text(file_path)
        
        # Get sections
        sections = self.get_sections(file_path)
        
        # Create metadata
        metadata = {
            "file_type": "text/plain",
            "file_size": os.path.getsize(file_path),
            "file_name": filename,
        }
        
        # Create result
        result = ParserResult(
            title=title,
            content=full_text,
            sections=sections,
            metadata=metadata
        )
        
        return result.to_dict()

    def get_full_text(self, file_path: str) -> str:
        """
        Extract the full text content from a text file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            The full text content as a string
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with another encoding if UTF-8 fails
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()

    def get_sections(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract sections from a text file based on heading patterns.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            A list of sections with titles and content
        """
        full_text = self.get_full_text(file_path)
        lines = full_text.splitlines()
        
        sections = []
        current_section: Optional[Dict[str, Any]] = None
        current_content = []
        
        for line in lines:
            is_heading = False
            heading_text = None
            
            # Check if line matches any heading pattern
            for pattern in self.heading_patterns:
                match = re.match(pattern, line.strip())
                if match:
                    is_heading = True
                    heading_text = match.group(1) if match.groups() else line.strip()
                    break
                    
            # If this is a heading, start a new section
            if is_heading:
                # Save previous section if it exists
                if current_section:
                    current_section["content"] = "\n".join(current_content).strip()
                    sections.append(current_section)
                
                # Start new section
                current_section = {
                    "title": heading_text or line.strip(),
                    "level": 1,  # Default level for text files
                    "content": ""
                }
                current_content = []
            else:
                # Add line to current section content
                current_content.append(line)
        
        # Save the last section
        if current_section:
            current_section["content"] = "\n".join(current_content).strip()
            sections.append(current_section)
        # If no sections were found, create a default section
        elif full_text.strip():
            sections.append({
                "title": "Content",
                "level": 1,
                "content": full_text.strip()
            })
            
        return sections
        
    def _clean_text(self, text: str) -> str:
        """
        Clean the text by removing extra whitespace and normalizing line breaks.
        
        Args:
            text: The text to clean
            
        Returns:
            The cleaned text
        """
        # Replace multiple newlines with a single newline
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Replace multiple spaces with a single space
        text = re.sub(r' {2,}', ' ', text)
        
        # Trim whitespace
        text = text.strip()
        
        return text 