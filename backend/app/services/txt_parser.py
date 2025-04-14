import logging
import os
import re
from typing import Dict, Any, List, Optional

from app.core.parser_interface import FileParserInterface, ParserResult

logger = logging.getLogger(__name__)


class TXTParser(FileParserInterface):
    """
    Parser for plain text files.
    """
    
    def __init__(self):
        """Initialize the TXT parser."""
        # Regex pattern to identify potential section titles in text files
        self.section_pattern = re.compile(r'^(?:\d+[\.\)]\s*)?([A-Z][^\.!?]*?)(?:\.|\:|\n|$)')
        
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
            logger.error(f"Error parsing text file {file_path}: {str(e)}")
            raise
    
    def get_full_text(self, file_path: str) -> str:
        """
        Extract the full text content from a text file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            The extracted text content
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                return file.read()
                
        except UnicodeDecodeError:
            # Try different encodings if UTF-8 fails
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                logger.error(f"Error reading text file with alternate encoding {file_path}: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Error extracting text from text file {file_path}: {str(e)}")
            raise
    
    def get_sections(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract sections from a text file using heuristic methods.
        
        Args:
            file_path: Path to the text file
            
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
            logger.error(f"Error extracting sections from text file {file_path}: {str(e)}")
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
                # Keep empty lines in the content but don't use them for section detection
                if current_section is not None and current_content:
                    current_content.append("")
                continue
                
            # Check if the line looks like a section heading
            match = self.section_pattern.match(line)
            is_uppercase_title = line.isupper() and len(line) < 100 and len(line.split()) <= 7
            
            if (match and len(line) < 100) or is_uppercase_title:
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
        Extract metadata from a text file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            A dictionary containing metadata
        """
        try:
            file_stats = os.stat(file_path)
            
            with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                content = file.read()
                
            metadata = {
                "file_size": file_stats.st_size,
                "created": file_stats.st_ctime,
                "modified": file_stats.st_mtime,
                "line_count": content.count('\n') + 1,
                "word_count": self._count_words(content),
                "char_count": len(content)
            }
            
            # Try to find title from first non-empty line
            lines = content.split('\n')
            for line in lines:
                if line.strip():
                    metadata["title"] = line.strip()[:100]  # Limit title length
                    break
                
            return metadata
                
        except Exception as e:
            logger.warning(f"Error extracting metadata from text file {file_path}: {str(e)}")
            # Return basic file metadata if extraction fails
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