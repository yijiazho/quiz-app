import os
import mimetypes
import logging
from typing import Dict, Any, Optional

from app.core.parser_interface import FileParserInterface
from app.services.text_parser import TextParser
# We'll import these once they're implemented
# from app.services.pdf_parser import PDFParser
# from app.services.docx_parser import DocxParser

logger = logging.getLogger(__name__)

# Ensure mimetype database is initialized
mimetypes.init()


class ParserFactory:
    """
    Factory for creating file parser instances based on file type.
    """
    
    @staticmethod
    def get_parser(file_path: str) -> Optional[FileParserInterface]:
        """
        Get the appropriate parser for a file based on its extension or mimetype.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            An instance of the appropriate parser, or None if no matching parser is found
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Get file extension and guess mimetype
        file_ext = os.path.splitext(file_path)[1].lower()
        mime_type, _ = mimetypes.guess_type(file_path)
        
        logger.info(f"Selecting parser for {file_path} with mime_type: {mime_type}, extension: {file_ext}")
        
        # Plain text files
        if file_ext in ['.txt'] or (mime_type and mime_type.startswith('text/')):
            return TextParser()
            
        # PDF files
        elif file_ext == '.pdf' or (mime_type and mime_type == 'application/pdf'):
            # Return PDFParser once implemented
            logger.warning("PDF parser not yet implemented, using text parser as fallback")
            return TextParser()
            
        # Word documents
        elif file_ext in ['.docx', '.doc'] or (mime_type and 'officedocument.wordprocessingml' in mime_type):
            # Return DocxParser once implemented
            logger.warning("DOCX parser not yet implemented, using text parser as fallback")
            return TextParser()
            
        # Unsupported file type
        else:
            logger.error(f"Unsupported file type: {file_ext} with mime type {mime_type}")
            return None
            
    @staticmethod
    def parse_file(file_path: str) -> Dict[str, Any]:
        """
        Parse a file using the appropriate parser.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            The parsed file content
            
        Raises:
            ValueError: If no suitable parser is found for the file type
        """
        parser = ParserFactory.get_parser(file_path)
        
        if parser:
            return parser.parse(file_path)
        else:
            raise ValueError(f"Unsupported file type: {os.path.splitext(file_path)[1]}")
            
    @staticmethod
    def get_supported_extensions() -> list:
        """
        Get a list of supported file extensions.
        
        Returns:
            A list of supported file extensions
        """
        return ['.txt', '.pdf', '.docx', '.doc'] 