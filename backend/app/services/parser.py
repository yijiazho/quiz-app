from typing import Dict, Any, Optional, Type
from .parser_interface import FileParserInterface
from .csv_parser import CSVParser
from .pdf_parser import PDFParser
from .docx_parser import DOCXParser
from .txt_parser import TXTParser
from .json_parser import JSONParser
import logging
import os

logger = logging.getLogger(__name__)

class ParserFactory:
    """Factory class for creating appropriate file parsers based on file extension"""
    
    # Map of file extensions to their corresponding parser classes
    PARSER_MAP: Dict[str, Type[FileParserInterface]] = {
        '.csv': CSVParser,
        '.pdf': PDFParser,
        '.docx': DOCXParser,
        '.doc': DOCXParser,
        '.txt': TXTParser,
        '.json': JSONParser
    }
    
    @classmethod
    def get_parser(cls, filepath: str) -> Optional[FileParserInterface]:
        """
        Get the appropriate parser for the given file
        
        Args:
            filepath: Path to the file to parse
            
        Returns:
            An instance of the appropriate parser, or None if no parser is available
        """
        try:
            # Get the file extension
            _, ext = os.path.splitext(filepath)
            ext = ext.lower()
            
            # Get the parser class from the map
            parser_class = cls.PARSER_MAP.get(ext)
            
            if parser_class is None:
                logger.warning(f"No parser available for file type: {ext}")
                return None
                
            # Create and return an instance of the parser
            return parser_class()
            
        except Exception as e:
            logger.error(f"Error getting parser for {filepath}: {str(e)}")
            return None 