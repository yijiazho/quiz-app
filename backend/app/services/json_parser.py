import json
import logging
import os
from typing import Dict, Any, List, Optional

from app.services.parser_interface import FileParserInterface, ParserResult

logger = logging.getLogger(__name__)


class JSONParser(FileParserInterface):
    """
    Parser for JSON (JavaScript Object Notation) files.
    """
    
    def __init__(self):
        """Initialize the JSON parser."""
        pass
        
    def parse(self, filepath: str) -> ParserResult:
        """
        Parse a JSON file and return its structured content
        
        Args:
            filepath: Path to the JSON file
            
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
            logger.error(f"Error parsing JSON file {filepath}: {str(e)}")
            raise
            
    def get_full_text(self, filepath: str) -> str:
        """
        Get the full text content of the file
        
        Args:
            filepath: Path to the JSON file
            
        Returns:
            String containing the full text content
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                # Try to parse and format JSON for better readability
                data = json.load(f)
                return json.dumps(data, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            # If JSON is invalid, return raw content
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Fallback to latin-1 if utf-8 fails
            with open(filepath, 'r', encoding='latin-1') as f:
                return f.read()
                
    def get_sections(self, filepath: str) -> Dict[str, str]:
        """
        Get sections from the JSON file based on its structure
        
        Args:
            filepath: Path to the JSON file
            
        Returns:
            Dictionary mapping section names to their content
        """
        sections = {}
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if isinstance(data, dict):
                # For objects, create sections for each top-level key
                for key, value in data.items():
                    sections[str(key)] = json.dumps(value, indent=2, ensure_ascii=False)
                    
            elif isinstance(data, list):
                # For arrays, create sections based on content type and size
                sections["Array Summary"] = f"Array with {len(data)} items"
                
                # Add sample items
                sample_size = min(5, len(data))
                if sample_size > 0:
                    sample = data[:sample_size]
                    sections["Sample Items"] = json.dumps(sample, indent=2, ensure_ascii=False)
                    
                # If items are objects, show schema
                if data and all(isinstance(item, dict) for item in data[:10]):
                    schema = set()
                    for item in data[:10]:  # Check first 10 items
                        schema.update(item.keys())
                    sections["Schema"] = "Common fields: " + ", ".join(sorted(schema))
                    
            else:
                # For primitive values, store as is
                sections["Content"] = json.dumps(data, indent=2, ensure_ascii=False)
                
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in file: {str(e)}")
            sections["Error"] = f"Invalid JSON: {str(e)}"
        except Exception as e:
            logger.warning(f"Error getting sections from JSON file: {str(e)}")
            
        return sections
        
    def _extract_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract metadata from the JSON file
        
        Args:
            filepath: Path to the JSON file
            
        Returns:
            Dictionary containing metadata about the file
        """
        try:
            file_stats = os.stat(filepath)
            
            metadata = {
                "file_size": file_stats.st_size,
                "created": file_stats.st_ctime,
                "modified": file_stats.st_mtime,
                "file_type": "application/json",
                "file_name": os.path.basename(filepath)
            }
            
            # Try to get JSON-specific metadata
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if isinstance(data, dict):
                    metadata.update({
                        "structure_type": "object",
                        "keys_count": len(data),
                        "top_level_keys": list(data.keys())
                    })
                elif isinstance(data, list):
                    metadata.update({
                        "structure_type": "array",
                        "items_count": len(data)
                    })
                else:
                    metadata["structure_type"] = type(data).__name__
                    
            except json.JSONDecodeError as e:
                metadata["parse_error"] = str(e)
            except Exception as e:
                logger.debug(f"Error extracting JSON metadata: {str(e)}")
                
            return metadata
            
        except Exception as e:
            logger.warning(f"Error extracting metadata from JSON file: {str(e)}")
            return {
                "file_size": os.path.getsize(filepath),
                "file_type": "application/json",
                "file_name": os.path.basename(filepath)
            } 