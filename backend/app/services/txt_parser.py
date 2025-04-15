import logging
import os
import re
from typing import Dict, Any, List, Optional

from app.services.parser_interface import FileParserInterface, ParserResult

logger = logging.getLogger(__name__)


class TXTParser(FileParserInterface):
    """
    Parser for plain text files.
    """
    
    def __init__(self):
        """Initialize the TXT parser."""
        # Regex pattern to identify potential section titles in text files
        self.section_pattern = re.compile(r'^(?:\d+[\.\)]\s*)?([A-Z][^\.!?]*?)(?:\.|\:|\n|$)')
        
    def parse(self, filepath: str) -> ParserResult:
        """
        Parse a text file and return its contents and metadata
        
        Args:
            filepath: Path to the text file
            
        Returns:
            ParserResult containing the parsed content, sections, and metadata
        """
        try:
            # Get the title from the filename
            title = os.path.splitext(os.path.basename(filepath))[0]
            
            # Get the content
            content = self.get_full_text(filepath)
            
            # Get sections
            sections = self.get_sections(filepath)
            
            # Get metadata
            metadata = self._extract_metadata(filepath)
            
            return ParserResult(
                title=title,
                content=content,
                sections=sections,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error parsing text file {filepath}: {str(e)}")
            raise
    
    def get_full_text(self, filepath: str) -> str:
        """
        Get the full text content of the file
        
        Args:
            filepath: Path to the text file
            
        Returns:
            The complete text content of the file
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Fallback to latin-1 if utf-8 fails
            with open(filepath, 'r', encoding='latin-1') as f:
                return f.read()
                
    def get_sections(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Get sections from the text file based on pattern matching
        
        Args:
            filepath: Path to the text file
            
        Returns:
            List of dictionaries containing section title and content
        """
        try:
            content = self.get_full_text(filepath)
            sections = []
            
            # Split content into lines
            lines = content.splitlines()
            
            current_section = {"title": "Main Content", "content": [], "level": 1}
            
            for line in lines:
                # Check if line matches section pattern
                match = self.section_pattern.match(line)
                
                if match:
                    # Save previous section if it has content
                    if current_section["content"]:
                        current_section["content"] = '\n'.join(current_section["content"])
                        sections.append(current_section)
                    
                    # Start new section
                    current_section = {
                        "title": match.group(1).strip(),
                        "content": [],
                        "level": 1
                    }
                else:
                    current_section["content"].append(line)
                    
            # Save last section
            if current_section["content"]:
                current_section["content"] = '\n'.join(current_section["content"])
                sections.append(current_section)
                
            # If no sections were found, use the entire content as one section
            if not sections:
                sections = [{
                    "title": "Main Content",
                    "content": content,
                    "level": 1
                }]
                
            return sections
            
        except Exception as e:
            logger.error(f"Error extracting sections from text file {filepath}: {str(e)}")
            raise
        
    def _extract_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract metadata from the text file
        
        Args:
            filepath: Path to the text file
            
        Returns:
            Dictionary containing metadata about the file
        """
        try:
            file_stats = os.stat(filepath)
            content = self.get_full_text(filepath)
            
            # Count lines, words, and characters
            lines = content.splitlines()
            words = content.split()
            
            metadata = {
                "file_size": file_stats.st_size,
                "created": file_stats.st_ctime,
                "modified": file_stats.st_mtime,
                "file_type": "text/plain",
                "file_name": os.path.basename(filepath),
                "line_count": len(lines),
                "word_count": len(words),
                "char_count": len(content)
            }
            
            return metadata
            
        except Exception as e:
            logger.warning(f"Error extracting metadata from text file: {str(e)}")
            return {
                "file_size": os.path.getsize(filepath),
                "file_type": "text/plain",
                "file_name": os.path.basename(filepath)
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