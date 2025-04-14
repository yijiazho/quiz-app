import json
import logging
import os
from typing import Dict, Any, List, Optional

from app.core.parser_interface import FileParserInterface, ParserResult

logger = logging.getLogger(__name__)


class JSONParser(FileParserInterface):
    """
    Parser for JSON (JavaScript Object Notation) files.
    """
    
    def __init__(self):
        """Initialize the JSON parser."""
        pass
        
    def parse(self, file_path: str) -> ParserResult:
        """
        Parse a JSON file and return its structured content.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            A ParserResult object containing the parsed content
        """
        logger.info(f"Parsing JSON file: {file_path}")
        
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
            logger.error(f"Error parsing JSON file {file_path}: {str(e)}")
            raise
    
    def get_full_text(self, file_path: str) -> str:
        """
        Extract the full text content from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
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
                logger.error(f"Error reading JSON file with alternate encoding {file_path}: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Error extracting text from JSON file {file_path}: {str(e)}")
            raise
    
    def get_sections(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract sections from a JSON file, treating top-level keys as sections.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            A list of sections, each containing title and content
        """
        try:
            # Parse JSON data
            json_data = self._parse_json_data(file_path)
            
            sections = []
            
            # Handle different types of JSON structures
            if isinstance(json_data, dict):
                # For objects, create sections from top-level keys
                for key, value in json_data.items():
                    section_content = self._format_json_value(value)
                    section = {
                        "title": str(key),
                        "content": section_content
                    }
                    sections.append(section)
                    
            elif isinstance(json_data, list):
                # For arrays, create sections for different array segments
                # Structure overview section
                structure_section = {
                    "title": "Structure",
                    "content": f"Array with {len(json_data)} elements"
                }
                sections.append(structure_section)
                
                # Sample items section
                max_items = min(10, len(json_data))
                if max_items > 0:
                    sample_items = json_data[:max_items]
                    sample_content = "\n\n".join([self._format_json_value(item, indent=2) for item in sample_items])
                    
                    sample_section = {
                        "title": f"Sample Items (1-{max_items})",
                        "content": sample_content
                    }
                    sections.append(sample_section)
                    
            else:
                # For simple values, create a single section
                sections.append({
                    "title": "Content",
                    "content": self._format_json_value(json_data)
                })
                
            # If no sections were created, add a fallback section with the raw content
            if not sections:
                full_text = self.get_full_text(file_path)
                sections = [{"title": "Content", "content": full_text}]
                
            return sections
            
        except Exception as e:
            logger.warning(f"Error extracting sections from JSON file {file_path}: {str(e)}")
            # Fallback to raw text
            full_text = self.get_full_text(file_path)
            return [{"title": "Content", "content": full_text}]
    
    def _parse_json_data(self, file_path: str) -> Any:
        """
        Parse JSON data from a file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Parsed JSON data (dict, list, or primitive values)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in {file_path}: {str(e)}")
            # Try to fix common JSON issues
            content = self.get_full_text(file_path)
            try:
                # Try with more lenient parser if available
                import jsonc_parser
                return jsonc_parser.parse_string(content)
            except (ImportError, Exception):
                # Last resort: try to remove comments and trailing commas
                import re
                # Remove JavaScript-style comments
                content = re.sub(r'//.*?$|/\*.*?\*/', '', content, flags=re.MULTILINE|re.DOTALL)
                # Remove trailing commas
                content = re.sub(r',\s*([}\]])', r'\1', content)
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    raise ValueError(f"Unable to parse JSON file: {file_path}")
    
    def _format_json_value(self, value: Any, indent: int = 0) -> str:
        """
        Format a JSON value as a readable string.
        
        Args:
            value: The JSON value to format
            indent: Number of spaces to indent
            
        Returns:
            Formatted string representation
        """
        if isinstance(value, (dict, list)):
            try:
                return json.dumps(value, indent=2, ensure_ascii=False)
            except Exception:
                return str(value)
        else:
            return str(value)
    
    def _extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            A dictionary containing metadata
        """
        try:
            file_stats = os.stat(file_path)
            
            # Basic file metadata
            metadata = {
                "file_size": file_stats.st_size,
                "created": file_stats.st_ctime,
                "modified": file_stats.st_mtime,
            }
            
            # Parse JSON to get structure information
            try:
                json_data = self._parse_json_data(file_path)
                
                if isinstance(json_data, dict):
                    metadata.update({
                        "structure_type": "object",
                        "keys_count": len(json_data),
                        "top_level_keys": list(json_data.keys())[:20]  # Limit to first 20 keys
                    })
                elif isinstance(json_data, list):
                    metadata.update({
                        "structure_type": "array",
                        "items_count": len(json_data)
                    })
                    
                    # Check if it's an array of objects with consistent schema
                    if json_data and all(isinstance(item, dict) for item in json_data[:10]):
                        sample_keys = set()
                        for item in json_data[:10]:
                            sample_keys.update(item.keys())
                        if sample_keys:
                            metadata["common_item_keys"] = list(sample_keys)
                else:
                    metadata["structure_type"] = type(json_data).__name__
                    
            except Exception as e:
                logger.debug(f"Error extracting JSON structure metadata: {str(e)}")
                
            return metadata
                
        except Exception as e:
            logger.warning(f"Error extracting metadata from JSON file {file_path}: {str(e)}")
            # Return basic file metadata if extraction fails
            return {
                "file_size": os.path.getsize(file_path)
            } 