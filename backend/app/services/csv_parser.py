import csv
import logging
import os
from typing import Dict, Any, List, Optional

from app.services.parser_interface import FileParserInterface, ParserResult

logger = logging.getLogger(__name__)


class CSVParser(FileParserInterface):
    """
    Parser for CSV (Comma-Separated Values) files.
    """
    
    def __init__(self):
        """Initialize the CSV parser."""
        pass
        
    def parse(self, file_path: str) -> ParserResult:
        """
        Parse a CSV file and return its structured content.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            A ParserResult object containing the parsed content
        """
        logger.info(f"Parsing CSV file: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            # Get the title from the filename
            title = os.path.splitext(os.path.basename(file_path))[0]
            
            # Get full text content
            content = self.get_full_text(file_path)
            
            # Get sections
            sections = self.get_sections(file_path)
            
            # Get metadata
            metadata = self._extract_metadata(file_path)
            
            return ParserResult(
                title=title,
                content=content,
                sections=sections,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error parsing CSV file {file_path}: {str(e)}")
            raise
            
    def get_full_text(self, file_path: str) -> str:
        """
        Get the full text content of the CSV file
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            String containing the full text content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Fallback to latin-1 if utf-8 fails
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
                
    def get_sections(self, file_path: str) -> Dict[str, str]:
        """
        Get sections from the CSV file
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Dictionary mapping section names to their content
        """
        sections = {}
        try:
            data = self._parse_csv_data(file_path)
            
            if not data:
                return sections
                
            # Add headers section
            if data[0]:
                sections['Headers'] = ', '.join(data[0])
                
            # Add data summary section
            if len(data) > 1:
                sample_rows = data[1:min(6, len(data))]  # Get up to 5 data rows
                sections['Data Sample'] = '\n'.join(
                    [', '.join(row) for row in sample_rows]
                )
                
            # Add statistics section
            sections['Statistics'] = f"""
Total Rows: {len(data) - 1}
Total Columns: {len(data[0]) if data else 0}
"""
            return sections
            
        except Exception as e:
            logger.warning(f"Error getting sections from CSV file: {str(e)}")
            return sections
            
    def _parse_csv_data(self, file_path: str) -> List[List[str]]:
        """
        Parse the CSV file and return its data
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List of rows, where each row is a list of strings
        """
        # Try different delimiters and encodings
        delimiters = [',', ';', '\t', '|']
        encodings = ['utf-8', 'latin-1']
        
        for encoding in encodings:
            for delimiter in delimiters:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        reader = csv.reader(f, delimiter=delimiter)
                        data = list(reader)
                        
                        # If we successfully read data with more than one column,
                        # assume we found the right delimiter
                        if data and len(data[0]) > 1:
                            return data
                            
                except Exception as e:
                    logger.debug(f"Failed to parse CSV with delimiter '{delimiter}' and encoding '{encoding}': {str(e)}")
                    continue
                    
        # If all attempts failed, try one last time with default settings
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return list(csv.reader(f))
        except Exception as e:
            logger.error(f"Failed to parse CSV file: {str(e)}")
            return []
            
    def _extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from the CSV file
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Dictionary containing metadata
        """
        try:
            file_stats = os.stat(file_path)
            
            metadata = {
                "file_size": file_stats.st_size,
                "created": file_stats.st_ctime,
                "modified": file_stats.st_mtime,
                "file_type": "text/csv",
                "file_name": os.path.basename(file_path)
            }
            
            # Try to get CSV-specific metadata
            try:
                data = self._parse_csv_data(file_path)
                if data:
                    metadata.update({
                        "row_count": len(data) - 1,  # Exclude header row
                        "column_count": len(data[0]) if data else 0,
                        "headers": data[0] if data else []
                    })
            except Exception as e:
                logger.debug(f"Error extracting CSV-specific metadata: {str(e)}")
                
            return metadata
                
        except Exception as e:
            logger.warning(f"Error extracting metadata from CSV file: {str(e)}")
            return {
                "file_size": os.path.getsize(file_path),
                "file_type": "text/csv",
                "file_name": os.path.basename(file_path)
            } 