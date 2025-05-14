from typing import Dict, Type
from .parser_interface import ParserInterface
from .pdf_parser import PDFParser
from .text_parser import TextParser

class ParserFactory:
    """Factory for creating appropriate parsers based on content type"""
    
    def __init__(self):
        """Initialize the parser factory with available parsers"""
        self._parsers: Dict[str, Type[ParserInterface]] = {
            'pdf': PDFParser,
            'text': TextParser
        }
    
    def get_parser(self, content_type: str) -> ParserInterface:
        """
        Get the appropriate parser for the given content type
        
        Args:
            content_type: The MIME type of the file
            
        Returns:
            An instance of the appropriate parser
            
        Raises:
            ValueError: If no parser supports the content type
        """
        for parser_class in self._parsers.values():
            parser = parser_class()
            if parser.supports_content_type(content_type):
                return parser
                
        raise ValueError(f"No parser available for content type: {content_type}")
    
    def register_parser(self, name: str, parser_class: Type[ParserInterface]):
        """
        Register a new parser
        
        Args:
            name: A unique name for the parser
            parser_class: The parser class to register
        """
        self._parsers[name] = parser_class 